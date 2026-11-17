"""Capture full read-only post-231 fsck diagnostics without repairing or booting."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settingsdata-repair-inspection-232'
REMOTE = r'''
from pathlib import Path
import hashlib,json,os,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/settingsdata-inspection-232')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
assert not mount.exists() and command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 image=mount/'harmony-settings-data-197/data.ext4'
 assert not image.is_symlink() and not command(['losetup','-j',str(image)]).strip()
 before=sha(image)
 check=subprocess.run(['e2fsck','-f','-n',str(image)],capture_output=True,text=True,timeout=180)
 rows=[]
 for path in paths:
  proc=subprocess.run(['debugfs','-R','stat /'+path,str(image)],capture_output=True,text=True,timeout=30)
  rows.append(dict(path=path,stdout=proc.stdout,stderr=proc.stderr,exit_status=proc.returncode))
 assert sha(image)==before
 active=mount/'harmony-persistent-data-165/data.ext4'
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 backup=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/settingsdata-repair-231')
 record=json.loads((backup/'backup.json').read_text())
 assert record['original_sha256']=='c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42' and record['decompressed_hash_verified']
 result=dict(candidate_sha256=before,fsck_exit=check.returncode,fsck_stdout=check.stdout,
  fsck_stderr=check.stderr,directory_metadata=rows,private_backup_verified_record=record,
  active165_unchanged=True,candidate_bytes_unchanged_by_inspection=True,
  repair_requested=False,boot_selected=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    source = json.loads((ROOT / 'reports/settingsdata-scaffolding-216/plan.json').read_text())
    code = 'paths=' + repr([row['path'] for row in source['directories']]) + '\n' + REMOTE
    REPORT.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=code,
        capture_output=True, text=True, timeout=600)
    if result.stderr:
        (REPORT / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    (REPORT / 'result.json').open('x').write(result.stdout)
    print(result.stdout)
