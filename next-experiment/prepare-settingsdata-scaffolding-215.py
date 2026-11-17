"""Prepare local empty provider directories from genuine installer metadata."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = Path('/home/zoinve/harmony-virgl-883')
WORK = BUILD / 'settingsdata-scaffolding-215'
REPORT = ROOT / 'reports/settingsdata-scaffolding-215'
SOURCE = BUILD / 'settings-data-candidate-191-r2/data.ext4'
SOURCE_SHA = 'f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce'
BASE = 'app/el1/0/base/com.ohos.settingsdata'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def plan():
    assert not REPORT.exists() and not WORK.exists(), 'immutable numbered output'
    source = json.loads((ROOT / 'reports/settingsdata-directories-214/source.json').read_text())
    target = json.loads((ROOT / 'reports/settingsdata-directories-214/target.json').read_text())
    absent = {row['path'] for row in target['directories'] if not row['present']}
    rows = [row for row in source['directory_metadata']
            if row['path'] == BASE or row['path'].startswith(BASE + '/')]
    assert len(rows) == 6 and all(row['path'] in absent for row in rows)
    assert all(row['uid'] == 20027 for row in rows)
    ancestors = set(str(parent) for parent in Path(BASE).parents if str(parent) != '.')
    rows += [row for row in source['directory_metadata'] if row['path'] in ancestors]
    assert ancestors <= {row['path'] for row in rows}
    owner = json.loads((ROOT / 'reports/settingsdata-owner-192/result.json').read_text())
    assert owner['settingsdata_records'][0]['users'] == [dict(user_id=0, uid=20027)]
    tools = BUILD / 'commercial61-tools-001/root'
    env = dict(os.environ, LD_LIBRARY_PATH=str(tools / 'usr/lib/x86_64-linux-gnu'))
    data = subprocess.check_output([str(tools / 'usr/bin/unsquashfs'), '-cat',
        str(BUILD / 'commercial61-iso-001/payload.squashfs'), 'state-labels.tsv'], env=env)
    labels = {}
    for row in csv.DictReader(io.StringIO(data.decode()), delimiter='\t'):
        path = row['path'].removeprefix('./.hmos-data/').removeprefix('.hmos-data/')
        if path in {item['path'] for item in rows}:
            assert path not in labels
            labels[path] = row['selinux']
    policy_record = json.loads((ROOT / 'reports/settings-state-labels-190/result.json').read_text())
    policy_file = BUILD / 'settings-state-labels-190/original-file-contexts'
    assert sha(policy_file) == policy_record['original_policy_sha256']
    policy = runpy.run_path(str(ROOT / 'next-experiment/complete-settings-state-labels-190.py'))['FilePolicy'](policy_file)
    try:
        for row in rows:
            path = row['path']
            row['selinux'] = labels.get(path) or policy.lookup('/data/' + path, stat.S_IFDIR | row['mode'])
            row['label_origin'] = 'original state-labels.tsv' if path in labels else 'original file_contexts'
            assert row['selinux'].startswith('u:object_r:')
    finally:
        policy.close()
    REPORT.mkdir()
    WORK.mkdir(mode=0o700)
    result = dict(directories=rows, source_image=str(SOURCE), source_sha256=SOURCE_SHA,
        state_labels_sha256=hashlib.sha256(data).hexdigest(),
        policy_sha256=policy_record['original_policy_sha256'],
        target_modified=False, usb_work_paused=True, app_file_contents_copied=False)
    (REPORT / 'plan.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


def fingerprint(root, excluded):
    digest = hashlib.sha256()
    count = 0
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root).as_posix()
        if relative in excluded:
            continue
        info = path.lstat()
        attributes = {name: os.getxattr(path, name, follow_symlinks=False).hex()
                      for name in sorted(os.listxattr(path, follow_symlinks=False))}
        row = [relative, stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode),
               info.st_uid, info.st_gid, attributes]
        if stat.S_ISREG(info.st_mode):
            row += [info.st_size, sha(path)]
        elif stat.S_ISLNK(info.st_mode):
            row += [os.readlink(path)]
        elif not stat.S_ISDIR(info.st_mode):
            row += [info.st_rdev]
        digest.update(json.dumps(row, sort_keys=True).encode() + b'\n')
        count += 1
    return dict(nodes=count, sha256=digest.hexdigest())


def prepare():
    assert os.geteuid() == 0, 'local WSL root only'
    record = json.loads((REPORT / 'plan.json').read_text())
    image = WORK / 'data.ext4'
    mount = WORK / 'mount'
    assert not image.exists() and not mount.exists() and not (REPORT / 'result.json').exists()
    assert not SOURCE.is_symlink() and sha(SOURCE) == SOURCE_SHA
    assert not subprocess.check_output(['losetup', '-j', str(SOURCE)]).strip()
    subprocess.run(['cp', '--reflink=auto', '--sparse=always', '--', str(SOURCE), str(image)], check=True)
    image.chmod(0o600)
    assert sha(image) == SOURCE_SHA
    subprocess.run(['tune2fs', '-U', 'random', str(image)], check=True, capture_output=True)
    mount.mkdir(mode=0o700)
    mounted = False
    paths = set()
    try:
        subprocess.run(['mount', '-t', 'ext4', '-o', 'loop,nodev,nosuid,noexec', str(image), str(mount)], check=True)
        mounted = True
        paths = {row['path'] for row in record['directories'] if not (mount / row['path']).exists()}
        assert BASE in paths
        before = fingerprint(mount, paths)
        for row in sorted(record['directories'], key=lambda item: (len(Path(item['path']).parts), item['path'])):
            path = mount / row['path']
            assert path.resolve().is_relative_to(mount.resolve()) and not path.parent.is_symlink()
            if row['path'] not in paths:
                assert path.is_dir() and not path.is_symlink()
                continue
            path.mkdir(mode=0o700)
            os.chown(path, row['uid'], row['gid'])
            os.chmod(path, row['mode'])
            os.setxattr(path, 'security.selinux', row['selinux'].encode() + b'\0')
            current = path.stat()
            assert (current.st_uid, current.st_gid, stat.S_IMODE(current.st_mode)) == (row['uid'], row['gid'], row['mode'])
            assert os.getxattr(path, 'security.selinux').rstrip(b'\0').decode() == row['selinux']
            assert path.is_dir()
        after = fingerprint(mount, paths)
        assert before == after, 'existing file bytes, owner, permissions, links and xattrs must remain intact'
        os.sync()
    finally:
        if mounted:
            subprocess.run(['umount', str(mount)], check=True)
        mount.rmdir()
    check = subprocess.run(['e2fsck', '-f', '-n', str(image)], capture_output=True, text=True)
    (REPORT / 'fsck.stdout').open('x').write(check.stdout)
    (REPORT / 'fsck.stderr').open('x').write(check.stderr)
    assert check.returncode == 0
    assert sha(SOURCE) == SOURCE_SHA
    result = dict(candidate_path=str(image), candidate_sha256=sha(image),
        candidate_uuid=subprocess.check_output(['blkid', '-p', '-s', 'UUID', '-o', 'value', str(image)], text=True).strip(),
        directories_created=len(paths), existing_tree_before=before, existing_tree_after=after,
        comparison_excludes_directory_timestamps=True, source_unchanged=True,
        candidate_unmounted=True, offline_fsck_status=check.returncode,
        target_modified=False, active_data165_modified=False, candidate_booted=False,
        settings_ui_verified=False, usb_work_paused=True)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    import sys
    assert sys.argv[1:] in [['plan'], ['prepare']]
    (plan if sys.argv[1] == 'plan' else prepare)()
