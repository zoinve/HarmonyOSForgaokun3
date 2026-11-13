"""Restore only the lab workspace mount after verifying trial001 evidence twice."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent.parent
saved = base / 'reports/baremetal-native-trial-001-evidence-immediate'
report = base / 'reports/baremetal-lab-workspace-rw-002.json'
assert not report.exists()
files = json.loads((saved / 'collection.json').read_text())['files']
assert len(files) == 20
for row in files:
    path = saved / row['path']
    assert path.stat().st_size == row['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
payload = r'''
from pathlib import Path
import hashlib,json,subprocess,os
mount=Path('/mnt/harmony-lab')
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
assert subprocess.check_output(['findmnt','-n','-o','SOURCE,UUID,FSTYPE','--target',str(mount)],text=True).split()==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098','ext4']
part=subprocess.check_output(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p4'],text=True).strip()
assert part=='24bd14b9-9d92-490a-ad15-a59c6b8e7cd9'
def verify():
 for row in files:
  relative=Path(row['path']);assert not relative.is_absolute() and '..' not in relative.parts
  p=mount/relative;assert not p.is_symlink() and p.is_file()
  assert p.stat().st_size==row['bytes']
  assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
verify()
before=subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target',str(mount)],text=True).strip()
assert 'ro' in before.split(',') and 'nodev' in before.split(',') and 'nosuid' in before.split(',')
# Restore the original preparation mount flags on this isolated filesystem only.
subprocess.run(['mount','-o','remount,rw,nodev,nosuid,exec',str(mount)],check=True)
after=subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target',str(mount)],text=True).strip()
assert 'rw' in after.split(',') and 'noexec' not in after.split(',')
assert 'nodev' in after.split(',') and 'nosuid' in after.split(',')
verify();os.sync()
print(json.dumps(dict(evidence_files_verified_before_after=len(files),mount_source='/dev/nvme0n1p4',
 before_options=before,after_options=after,boot_entries_modified=False,reboot_requested=False),indent=2))
'''
p = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'],
                   input='files=' + repr(files) + '\n' + payload,
                   text=True, capture_output=True, timeout=60)
p.check_returncode()
result = json.loads(p.stdout)
report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(p.stdout)
