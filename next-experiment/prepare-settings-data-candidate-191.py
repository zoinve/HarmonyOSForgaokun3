'''Build an isolated local data image; never replace active data165 or boot it.'''
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import sqlite3
import stat
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
WORK = Path('/home/zoinve/harmony-virgl-883/settings-data-candidate-191')
REPORT = ROOT / 'reports/settings-data-candidate-191'
SEED_SHA = '02c810f94799cf4b89cc59dea2409981b4678e8b201d60c0ceb62fd7397b21cd'
REMOTE_SEED = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/oobe-seed-123/seed.ext4'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def settingsdata_registration(connection):
    traverse = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-coherence-188.py')))['dicts']
    found = set()
    for key, value in connection.execute('SELECT KEY, VALUE FROM installed_bundle'):
        if not re.fullmatch(r'com\.ohos\.settingsdata(?:_\d+)?', key):
            continue
        nodes = list(traverse(json.loads(value)))
        assert any(node.get('singleton') is True for node in nodes), 'user0 provider must be original singleton'
        for node in nodes:
            user = node.get('bundleUserInfo')
            if isinstance(user, dict) and user.get('userId') == 0:
                uid = node.get('uid')
                token = node.get('accessTokenId')
                assert isinstance(uid, int) and not isinstance(uid, bool) and uid > 0
                assert isinstance(token, int) and not isinstance(token, bool) and token > 0
                found.add((uid, token))
    assert len(found) == 1, 'need exact original SettingsData singleton registration for user0'
    uid, token = found.pop()
    return dict(uid=uid, private_token=token)


def settingsdata_uid(connection):
    return settingsdata_registration(connection)['uid']


def safe_member(root, relative):
    assert relative and not Path(relative).is_absolute() and '..' not in Path(relative).parts
    path = root / relative
    assert path.resolve().is_relative_to(root.resolve())
    assert not any(parent.is_symlink() for parent in [path, *path.parents] if parent.is_relative_to(root))
    return path


def stage():
    assert not WORK.exists() and not REPORT.exists(), 'preserve numbered staging'
    source = json.loads((ROOT / 'reports/oobe-seed-preparation-123/result.json').read_text())
    assert source['seed_sha256'] == SEED_SHA and source['seed_path'] == REMOTE_SEED
    WORK.mkdir(mode=0o700)
    REPORT.mkdir()
    seed = WORK / 'verified-seed123.ext4'
    code = '''
import hashlib,os,stat,sys
from pathlib import Path
assert 'ID=ubuntu' in Path('/etc/os-release').read_text().splitlines()
fd=os.open(PATH,os.O_RDONLY|os.O_NOFOLLOW)
with os.fdopen(fd,'rb') as stream:
 state=os.fstat(stream.fileno())
 assert stat.S_ISREG(state.st_mode) and state.st_size==536870912
 assert hashlib.file_digest(stream,'sha256').hexdigest()==EXPECTED
 stream.seek(0)
 while chunk:=stream.read(1024*1024):sys.stdout.buffer.write(chunk)
sys.stdout.buffer.flush()
'''
    code = 'PATH=' + repr(REMOTE_SEED) + '\nEXPECTED=' + repr(SEED_SHA) + '\n' + code
    args = ['/mnt/c/Windows/System32/OpenSSH/ssh.exe', '-i',
            'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
            '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostKeyAlias=192.168.10.128', '-o', 'ConnectTimeout=8',
            'zoinve@192.168.10.128', 'sudo -n python3 -']
    with seed.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        result = subprocess.run(args, input=code.encode(), stdout=stream, stderr=subprocess.PIPE, timeout=180)
        stream.flush()
        os.fsync(stream.fileno())
    assert result.returncode == 0, 'read-only authenticated seed transfer failed'
    assert seed.stat().st_size == 536870912 and sha(seed) == SEED_SHA
    record = dict(source_seed=REMOTE_SEED, seed_sha256=SEED_SHA,
                  authenticated_ssh_verified=True, remote_seed_read_only=True,
                  raw_seed_not_exported_to_reports=True, target_modified=False)
    with (REPORT / 'stage.json').open('x') as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps(record, indent=2))


def populate(seed_override=None):
    assert os.geteuid() == 0, 'use explicit local WSL root only for the isolated candidate mount'
    seed = seed_override or WORK / 'verified-seed123.ext4'
    candidate = WORK / 'data.ext4'
    mount = WORK / 'mount'
    assert (REPORT / 'stage.json').is_file() and not (REPORT / 'result.json').exists()
    assert not candidate.exists() and not mount.exists(), 'never overwrite an existing candidate'
    assert WORK.resolve() == WORK and WORK.is_dir() and not WORK.is_symlink()
    assert sha(seed) == SEED_SHA
    archive_record = json.loads((ROOT / 'reports/settings-preinstall-state-189/result.json').read_text())
    labels_record = json.loads((ROOT / 'reports/settings-state-labels-190/result.json').read_text())
    archive = Path(archive_record['archive'])
    labels = Path(labels_record['complete_labels_path'])
    assert sha(archive) == archive_record['archive_sha256']
    assert sha(labels) == labels_record['complete_labels_sha256']
    assert labels_record['all_candidate_members_have_labels']
    subprocess.run(['cp', '--sparse=always', '--reflink=never', str(seed), str(candidate)], check=True)
    os.chmod(candidate, 0o600)
    os.truncate(candidate, 8589934592)
    for label, command in [('pre-resize-fsck', ['e2fsck', '-f', '-p', str(candidate)]),
                           ('resize', ['resize2fs', str(candidate)])]:
        process = subprocess.run(command, capture_output=True, timeout=120)
        (REPORT / (label + '.stdout')).open('xb').write(process.stdout)
        (REPORT / (label + '.stderr')).open('xb').write(process.stderr)
        assert process.returncode == 0, (label, process.returncode, process.stderr.decode(errors='replace'))
    identity = str(uuid.uuid4())
    subprocess.run(['tune2fs', '-U', identity, str(candidate)], capture_output=True, check=True)
    mount.mkdir(mode=0o700)
    mounted = False
    checks = {}
    try:
        subprocess.run(['mount', '-t', 'ext4', '-o', 'loop,nodev,nosuid,noexec', str(candidate), str(mount)], check=True)
        mounted = True
        filesystem = json.loads(subprocess.check_output(['findmnt', '--json', '-o', 'TARGET,SOURCE,FSTYPE,UUID',
                                                       '--target', str(mount)], text=True))['filesystems'][0]
        assert filesystem['target'] == str(mount) and filesystem['fstype'] == 'ext4' and filesystem['uuid'] == identity
        loop = json.loads(subprocess.check_output(['losetup', '--json', '--output', 'NAME,BACK-FILE',
                                                  filesystem['source']], text=True))['loopdevices'][0]
        assert loop['back-file'] == str(candidate), 'only this new local backing file may be mounted'
        subprocess.run(['tar', '--numeric-owner', '--xattrs', '--xattrs-include=*', '--acls',
                        '--delay-directory-restore', '-xzf', str(archive), '-C', str(mount)], check=True)
        for row in archive_record['members']:
            path = safe_member(mount, row['path'])
            state = path.stat()
            assert (state.st_uid, state.st_gid, stat.S_IMODE(state.st_mode)) == (row['uid'], row['gid'], row['mode'])
            if row['kind'] == 0o100000:
                assert stat.S_ISREG(state.st_mode) and sha(path) == row['sha256']
            else:
                assert stat.S_ISDIR(state.st_mode)
        with labels.open(newline='') as stream:
            label_rows = list(csv.DictReader(stream, delimiter='\t'))
        for row in label_rows:
            path = safe_member(mount, row['path'])
            expected = row['selinux'].encode()
            os.setxattr(path, 'security.selinux', expected, follow_symlinks=False)
            assert os.getxattr(path, 'security.selinux', follow_symlinks=False) == expected
        database = safe_member(mount, 'service/el1/public/bms/bundle_manager_service/bmsdb.db')
        connection = sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True)
        try:
            connection.execute('PRAGMA query_only=ON')
            registration = settingsdata_registration(connection)
            owner = registration['uid']
        finally:
            connection.close()
        token_path = safe_member(mount, 'service/el1/public/access_token/access_token.db')
        connection = sqlite3.connect(token_path.as_uri() + '?mode=ro&immutable=1', uri=True)
        try:
            connection.execute('PRAGMA query_only=ON')
            token_rows = connection.execute(
                'SELECT token_id FROM hap_token_info_table WHERE bundle_name=? AND user_id=?',
                ('com.ohos.settingsdata', 0)).fetchall()
            assert token_rows == [(registration['private_token'],)], 'source singleton token mismatch'
        finally:
            connection.close()
        metadata = json.loads((ROOT / 'reports/oobe-seed-preparation-123/result.json').read_text())
        package = safe_member(mount, 'app/el1/0/database/com.ohos.settingsdata')
        original_owner = metadata['databases'][0]['uid']
        assert all(row['uid'] == original_owner for row in metadata['databases'])
        changed = 0
        for path in [package, *package.rglob('*')]:
            safe_member(mount, str(path.relative_to(mount)))
            if path.stat().st_uid == original_owner and owner != original_owner:
                os.chown(path, owner, -1)
                changed += 1
        for row in metadata['databases']:
            path = safe_member(mount, 'app/el1/0/database/com.ohos.settingsdata/entry/rdb/' + row['name'])
            assert sha(path) == row['sha256'] and path.stat().st_uid == owner
        checks.update(source_members_verified=len(archive_record['members']), source_labels_verified=len(label_rows),
                      settingsdata_original_uid=original_owner, settingsdata_source_registry_uid=owner,
                      settingsdata_nodes_reowned_from_actual_registry=changed,
                      settingsdata_singleton_user_id=0, settingsdata_source_token_pair_verified=True,
                      existing_settingsdata_bytes_unchanged=True, original_bms_token_databases_unmodified=True)
        fd = os.open(mount, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        os.sync()
    finally:
        if mounted:
            subprocess.run(['umount', str(mount)], check=True)
    fsck = subprocess.run(['e2fsck', '-f', '-n', str(candidate)], capture_output=True)
    (REPORT / 'fsck.stdout').open('xb').write(fsck.stdout)
    (REPORT / 'fsck.stderr').open('xb').write(fsck.stderr)
    assert fsck.returncode == 0
    assert sha(seed) == SEED_SHA
    result = dict(candidate_path=str(candidate), candidate_bytes=candidate.stat().st_size,
                  candidate_uuid=identity, candidate_sha256=sha(candidate), offline_fsck_status=fsck.returncode,
                  **checks, source_seed_unchanged=True, candidate_unmounted=True,
                  target_modified=False, active_persistent_data165_modified=False,
                  original_images_modified=False, original_signature_checks_changed=False,
                  candidate_installed_or_booted=False, settings_ui_verified=False, usb_work_paused=True)
    result['local_allocated_bytes'] = candidate.stat().st_blocks * 512
    result['target_must_fully_allocate_before_existing_persistent_guard'] = True
    with (REPORT / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    assert sys.argv[1:] in [['--stage'], ['--populate'], ['--populate-r1'], ['--populate-r2']]
    if sys.argv[1] == '--stage':
        stage()
    elif sys.argv[1] == '--populate':
        populate()
    else:
        assert os.geteuid() == 0
        previous_work, previous_report = WORK, REPORT
        seed = previous_work / 'verified-seed123.ext4'
        assert sha(seed) == SEED_SHA and (previous_report / 'stage.json').is_file()
        revision = sys.argv[1].removeprefix('--populate-')
        if revision == 'r2':
            previous_work = previous_work.with_name(previous_work.name + '-r1')
            previous_report = previous_report.with_name(previous_report.name + '-r1')
        assert (previous_work / 'data.ext4').is_file() and not (previous_report / 'result.json').exists()
        assert not subprocess.check_output(['losetup', '-j', str(previous_work / 'data.ext4')]).strip()
        failure = dict(operation='local resize2fs before candidate mount' if revision == 'r1'
                       else 'original SettingsData singleton owner guard rejected incorrect user100 scope', exit_status=1,
                       stderr_not_saved_by_initial_invocation=True, candidate_mount_attempted=False,
                       target_modified=False, source_seed_changed=False, failed_candidate_preserved=True,
                       subsequent_root_read_only_e2fsck_status=0)
        if revision == 'r2':
            failure.update(stderr_not_saved_by_initial_invocation=False, candidate_mount_attempted=True,
                           candidate_unmounted_verified=True, subsequent_root_read_only_e2fsck_status=None,
                           actual_provider_user0_evidence='reports/settingsdata-owner-192/result.json')
        with (previous_report / 'initial-populate-failure.json').open('x') as stream:
            json.dump(failure, stream, indent=2)
        WORK = WORK.with_name(WORK.name + '-' + revision)
        REPORT = REPORT.with_name(REPORT.name + '-' + revision)
        assert not WORK.exists() and not REPORT.exists()
        WORK.mkdir(mode=0o700)
        REPORT.mkdir()
        record = dict(reused_verified_seed=str(seed), seed_sha256=SEED_SHA,
                      previous_candidate_preserved=True,
                      previous_resize_exit_status=1 if revision == 'r1' else None,
                      pre_resize_check_matches_existing_prepare165=True,
                      previous_stage_sha256=sha(previous_report / 'stage.json'), target_modified=False)
        with (REPORT / 'stage.json').open('x') as stream:
            json.dump(record, stream, indent=2)
        populate(seed_override=seed)
