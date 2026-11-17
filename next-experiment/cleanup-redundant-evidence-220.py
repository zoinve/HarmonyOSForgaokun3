"""User-authorized cleanup: keep final cumulative logs and canonical manifests."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/evidence-cleanup-220'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def plan():
    assert not REPORT.exists()
    REPORT.mkdir()
    rows = {}
    hashes = []
    manifests = list((ROOT / 'reports').glob('*/runtime-evidence/retrieval-manifest.json'))
    for manifest in manifests:
        source = json.loads(manifest.read_text())
        run = source.get('run', '')
        if not re.fullmatch(r'(?:commercial61-native|native-interactive)-[0-9]{3}-[0-9a-f-]{36}', run):
            continue
        files = source.get('files', {})
        if not isinstance(files, dict):
            continue
        for name, metadata in files.items():
            if not re.fullmatch(r'[A-Za-z0-9_.-]+\.log', name) or not isinstance(metadata, dict):
                continue
            path = manifest.parent / 'raw' / name
            if not path.is_file() or path.is_symlink():
                continue
            if path.stat().st_size != metadata.get('bytes') or sha(path) != metadata.get('sha256'):
                continue
            key = run + '/' + name
            rows[key] = dict(bytes=metadata['bytes'], sha256=metadata['sha256'],
                             local=str(path.relative_to(ROOT)))
    for path in (ROOT / 'reports').rglob('*'):
        if path.is_file() and ('hash' in path.name.lower() or 'manifest' in path.name.lower()):
            hashes.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size))
    result = dict(remote_logs=rows, hash_table_files=len(hashes),
                  hash_table_bytes=sum(row['bytes'] for row in hashes),
                  largest_hash_tables=sorted(hashes, key=lambda row: row['bytes'], reverse=True)[:25])
    with gzip.open(REPORT / 'verified-local-copies.json.gz', 'xt') as stream:
        json.dump(result, stream, separators=(',', ':'))
    print(json.dumps(dict(verified_remote_log_candidates=len(rows),
        verified_log_bytes=sum(row['bytes'] for row in rows.values()),
        hash_table_files=result['hash_table_files'], hash_table_bytes=result['hash_table_bytes'],
        largest_hash_tables=result['largest_hash_tables']), indent=2), flush=True)


REMOTE = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/evidence-cleanup-220')
assert os.geteuid()==0 and not mount.exists()
assert subprocess.check_output(['blkid','-p','-s','UUID','-o','value',device],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert 'Current Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in subprocess.check_output(['bootctl','status','--no-pager'],text=True)
mount.mkdir(mode=0o700);mounted=False
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 before=shutil.disk_usage(mount).free;removed=0;logical=0;allocated=0;missing=0;mismatch=0
 for relative,row in rows.items():
  path=mount/relative
  assert len(Path(relative).parts)==2 and path.resolve().is_relative_to(mount.resolve())
  assert not path.parent.is_symlink() and not path.is_symlink()
  if not path.exists():missing+=1;continue
  assert path.is_file()
  info=path.stat()
  if info.st_size!=row['bytes'] or sha(path)!=row['sha256']:mismatch+=1;continue
  path.unlink();removed+=1;logical+=info.st_size;allocated+=info.st_blocks*512
 os.sync()
 result=dict(removed_files=removed,removed_logical_bytes=logical,removed_allocated_bytes=allocated,
  already_missing=missing,hash_mismatch_retained=mismatch,free_before=before,
  free_after=shutil.disk_usage(mount).free,only_locally_hash_verified_log_copies_deleted=True,
  active_data_images_modified=False,original_images_modified=False,boot_entries_modified=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


def remote():
    output = REPORT / 'remote.json'
    assert not output.exists() and not (REPORT / 'remote.stderr').exists()
    with gzip.open(REPORT / 'verified-local-copies.json.gz', 'rt') as stream:
        rows = json.load(stream)['remote_logs']
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    code = 'rows=' + repr(rows) + '\n' + REMOTE
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=code,
        capture_output=True, text=True, timeout=1800)
    (REPORT / 'remote.stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    output.open('x').write(result.stdout)
    print(result.stdout)


def local():
    assert (REPORT / 'remote.json').is_file() and not (REPORT / 'local.json').exists()
    result = dict(removed_files=0, removed_bytes=0, cumulative_log_redirects=[])
    for raw in sorted((ROOT / 'reports').glob('*/runtime-evidence/raw')):
        assert raw.resolve().is_relative_to((ROOT / 'reports').resolve()) and not raw.is_symlink()
        files = [path for path in raw.glob('phase-*.log') if re.fullmatch(r'phase-[0-9]+\.log', path.name)]
        if len(files) < 2:
            continue
        final = max(files, key=lambda path: (path.stat().st_size, path.name))
        data = final.read_bytes()
        removed = []
        for path in files:
            assert not path.is_symlink() and path.resolve().parent == raw.resolve()
            if path == final:
                continue
            content = path.read_bytes()
            if data.startswith(content):
                path.unlink()
                removed.append(path.name)
                result['removed_files'] += 1
                result['removed_bytes'] += len(content)
        if removed:
            result['cumulative_log_redirects'].append(dict(directory=str(raw.relative_to(ROOT)),
                retained=final.name, removed=removed,
                reconstruction='retained file prefix with original byte length from retrieval-manifest.json'))
    (REPORT / 'local.json').open('x').write(json.dumps(result, separators=(',', ':')))
    print(json.dumps({key: value for key, value in result.items() if key != 'cumulative_log_redirects'}, indent=2))


if __name__ == '__main__':
    assert sys.argv[1:] in [['plan'], ['remote'], ['local']]
    dict(plan=plan, remote=remote, local=local)[sys.argv[1]]()
