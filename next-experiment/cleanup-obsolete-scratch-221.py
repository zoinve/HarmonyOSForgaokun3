"""Remove explicitly obsolete scratch images, never originals or active data."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import json,os,shutil,stat,subprocess
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')
names=['evidence-recovery-030/lab-raw.img',
 'oobe-snapshot-inspection-122/data-working.ext4',
 'official-arm-sdk-921/full-system-962/userdata-permissive.img']
assert os.geteuid()==0 and root.resolve()==root and not root.is_symlink()
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
paths=[root/name for name in names]
for path in paths:
 assert path.resolve().is_relative_to(root) and not path.is_symlink()
 assert all(not parent.is_symlink() for parent in path.parents)
 assert not subprocess.check_output(['losetup','-j',str(path)],text=True).strip()
 for line in Path('/proc/self/mountinfo').read_text().splitlines():
  assert str(path) not in line
for process in Path('/proc').iterdir():
 if not process.name.isdigit():continue
 try:
  command=(process/'cmdline').read_bytes()
  assert not any(str(path).encode() in command for path in paths),('active process',process.name)
  for fd in (process/'fd').iterdir():
   try:assert os.readlink(fd) not in {str(path) for path in paths},('open file',process.name)
   except (FileNotFoundError,ProcessLookupError):pass
 except (FileNotFoundError,ProcessLookupError):pass
before=shutil.disk_usage(root).free;removed=[]
for path in paths:
 if not path.exists():continue
 info=path.stat();assert stat.S_ISREG(info.st_mode)
 assert info.st_size>=1024**3
 path.unlink()
 removed.append(dict(path=str(path.relative_to(root)),bytes=info.st_size,allocated_bytes=info.st_blocks*512))
os.sync()
print(json.dumps(dict(removed=removed,free_before=before,free_after=shutil.disk_usage(root).free,
 original_images_deleted=False,boot_entries_modified=False,active_data165_modified=False),indent=2))
'''

if __name__ == '__main__':
    report = ROOT / 'reports/scratch-cleanup-221'
    assert not report.exists()
    report.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=REMOTE,
        capture_output=True, text=True, timeout=180)
    for suffix, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (report / suffix).open('x').write(data)
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    (report / 'result.json').open('x').write(json.dumps(record, indent=2))
    print(result.stdout)
