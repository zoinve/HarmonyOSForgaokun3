"""User-authorized removal of obsolete runtime logs and retired OOBE scratch."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'''
from pathlib import Path
import hashlib,json,os,re,shutil,stat,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/obsolete-lab-cleanup-224')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
assert os.geteuid()==0 and not mount.exists()
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
firmware=command(['efibootmgr','-v'])
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 pinned={'harmony-persistent-data-165/data.ext4':'36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce',
 'harmony-settings-data-197/data.ext4':'c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42'}
 for name,digest in pinned.items():
  path=mount/name
  assert path.is_file() and not path.is_symlink() and not path.parent.is_symlink()
  assert sha(path)==digest and not command(['losetup','-j',str(path)]).strip()
 before=shutil.disk_usage(mount).free;removed=0;allocated=0;logical=0;directories=0
 for directory in sorted(mount.iterdir()):
  if not re.fullmatch(r'(?:commercial61-native|native-interactive)-[0-9]{3}-[0-9a-f-]{36}',directory.name):continue
  assert directory.is_dir() and not directory.is_symlink() and directory.resolve().parent==mount.resolve()
  for path in sorted(directory.iterdir()):
   if path.suffix!='.log':continue
   assert not path.is_symlink() and path.is_file() and path.resolve().parent==directory.resolve()
   info=path.stat();path.unlink();removed+=1;logical+=info.st_size;allocated+=info.st_blocks*512
  if not any(directory.iterdir()):directory.rmdir();directories+=1
 retired=[]
 for relative in ['private-oobe121/data.ext4','harmony-settings-data-197-incomplete-198-r1/data.ext4']:
  path=mount/relative
  if not path.exists():continue
  assert path.resolve().is_relative_to(mount.resolve()) and not path.is_symlink() and not path.parent.is_symlink()
  assert path.is_file() and path.stat().st_size==8589934592
  assert not command(['losetup','-j',str(path)]).strip()
  info=path.stat();path.unlink()
  retired.append(dict(path=relative,allocated_bytes=info.st_blocks*512))
 for name,digest in pinned.items():assert sha(mount/name)==digest
 os.sync()
 result=dict(obsolete_log_files_deleted=removed,obsolete_log_logical_bytes=logical,
  obsolete_log_allocated_bytes=allocated,empty_run_directories_deleted=directories,
  retired_scratch_images_deleted=retired,free_before=before,free_after=shutil.disk_usage(mount).free,
  active165_sha256_verified=True,current197_sha256_verified=True,original_images_deleted=False,
  boot_entries_modified=False,old_log_deletion_explicitly_authorized=True)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
assert command(['efibootmgr','-v'])==firmware
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    report = ROOT / 'reports/obsolete-lab-cleanup-224'
    assert not report.exists()
    report.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=REMOTE,
        capture_output=True, text=True, timeout=600)
    (report / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    (report / 'result.json').open('x').write(result.stdout)
    print(result.stdout)
