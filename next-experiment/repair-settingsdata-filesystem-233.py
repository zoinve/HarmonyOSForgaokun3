"""Conservative offline preen, guarded by a private backup and tree equality."""
from pathlib import Path
import inspect
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settingsdata-filesystem-repair-233'
REMOTE = r'''
device='/dev/nvme0n1p4';mount=Path('/mnt/settingsdata-fsck-233')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
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
 image=mount/'harmony-settings-data-197/data.ext4';active=mount/'harmony-persistent-data-165/data.ext4'
 for path in [image,active]:
  assert path.is_file() and not path.is_symlink() and not path.parent.is_symlink()
  assert path.stat().st_size==8589934592 and not command(['losetup','-j',str(path)]).strip()
 assert sha(image)==expected
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 backup=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/settingsdata-repair-231')
 record=json.loads((backup/'backup.json').read_text())
 assert record['decompressed_hash_verified'] and record['original_sha256']=='c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42'
 assert (backup/'data-before.ext4.gz').stat().st_size==record['compressed_bytes']
 def tree():
  target=mount/'readonly-tree-233';assert not target.exists();target.mkdir(mode=0o700);inner=False
  try:
   subprocess.run(['mount','-t','ext4','-o','loop,ro,noload,nodev,nosuid,noexec',str(image),str(target)],check=True);inner=True
   return fingerprint(target,set())
  finally:
   if inner:subprocess.run(['umount',str(target)],check=True)
   target.rmdir()
 before=tree();assert sha(image)==expected
 env=dict(os.environ,LC_ALL='C')
 preen=subprocess.run(['e2fsck','-f','-p',str(image)],capture_output=True,text=True,timeout=240,env=env)
 (backup/'preen233.json').open('x').write(json.dumps(dict(exit_status=preen.returncode,stdout=preen.stdout,stderr=preen.stderr)))
 assert preen.returncode in [0,1],preen.stdout+preen.stderr
 check=subprocess.run(['e2fsck','-f','-n',str(image)],capture_output=True,text=True,timeout=240,env=env)
 assert check.returncode==0,check.stdout+check.stderr
 after=tree();assert before==after,'visible file bytes and metadata must remain unchanged'
 final=sha(image)
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 assert image.stat().st_blocks*512>=8589934592
 result=dict(data_path='/mnt/lab/harmony-settings-data-197/data.ext4',candidate_before_sha256=expected,
  candidate_after_sha256=final,filesystem_uuid='b8383c4f-844b-46cc-9d67-34a3745b3f1f',
  preen_exit=preen.returncode,preen_stdout=preen.stdout,preen_stderr=preen.stderr,
  final_read_only_fsck_exit=check.returncode,final_fsck_stdout=check.stdout,
  existing_tree_before=before,existing_tree_after=after,tree_comparison_excludes_timestamps=True,
  active165_sha256_verified_unchanged=True,original_images_modified=False,
  private_pre231_backup_retained=True,raw_app_state_exported=False,
  directory_scaffolding_source='reports/settingsdata-scaffolding-216/plan.json',
  boot_selected=False,settings_ui_verified=False,usb_work_paused=True)
 (backup/'repair233.json').open('x').write(json.dumps(result,indent=2));os.sync()
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
    assert not REPORT.exists()
    inspection = json.loads((ROOT / 'reports/settingsdata-repair-inspection-232/result.json').read_text())
    assert inspection['fsck_exit'] == 4 and inspection['candidate_bytes_unchanged_by_inspection']
    helper = runpy.run_path(str(ROOT / 'next-experiment/prepare-settingsdata-scaffolding-215.py'))
    code = ('from pathlib import Path\nimport hashlib,json,os,stat,subprocess\n' +
        inspect.getsource(helper['sha']) + '\n' + inspect.getsource(helper['fingerprint']) + '\n' +
        'expected=' + repr(inspection['candidate_sha256']) + '\n' + REMOTE)
    compile(code, 'settingsdata-preen233-remote', 'exec')
    REPORT.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=code,
        capture_output=True, text=True, timeout=1200)
    if result.stderr:
        (REPORT / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    (REPORT / 'result.json').open('x').write(result.stdout)
    print(result.stdout)
