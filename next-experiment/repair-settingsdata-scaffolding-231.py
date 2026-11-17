"""Back up and repair only original empty directories on isolated data197."""
from pathlib import Path
import inspect
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settingsdata-repair-231'
EXPECTED = 'c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42'
REMOTE = r'''
device='/dev/nvme0n1p4';mount=Path('/mnt/settingsdata-repair-231')
backup_root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/settingsdata-repair-231')
assert os.geteuid()==0 and not mount.exists() and not backup_root.exists()
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
firmware=command(['efibootmgr','-v'])
mount.mkdir(mode=0o700);outer=False;inner=False;data_mount=mount/'repair-data-mount-231'
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(mount)],check=True);outer=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 image=mount/'harmony-settings-data-197/data.ext4'
 active=mount/'harmony-persistent-data-165/data.ext4'
 for path in [image,active]:
  assert path.is_file() and not path.is_symlink() and not path.parent.is_symlink()
  assert path.stat().st_size==8589934592 and not command(['losetup','-j',str(path)]).strip()
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 assert sha(image)==expected and image.stat().st_blocks*512>=8589934592
 assert command(['blkid','-p','-s','UUID','-o','value',str(image)]).strip()=='b8383c4f-844b-46cc-9d67-34a3745b3f1f'
 check=subprocess.run(['e2fsck','-f','-n',str(image)],capture_output=True,text=True,timeout=180)
 assert check.returncode==0,check.stderr
 assert shutil.disk_usage(backup_root.parent).free>8589934592+1073741824
 backup_root.mkdir(mode=0o700);backup=backup_root/'data-before.ext4.gz'
 with image.open('rb') as source,backup.open('xb') as dest:
  os.fchmod(dest.fileno(),0o600)
  with gzip.GzipFile(filename='',fileobj=dest,mode='wb',compresslevel=1,mtime=0) as compressor:
   shutil.copyfileobj(source,compressor,1024**2)
  dest.flush();os.fsync(dest.fileno())
 with gzip.open(backup,'rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==expected
 assert sha(image)==expected
 (backup_root/'backup.json').open('x').write(json.dumps(dict(original_sha256=expected,
  compressed_bytes=backup.stat().st_size,decompressed_hash_verified=True,raw_app_state_exported=False)))
 data_mount.mkdir(mode=0o700)
 subprocess.run(['mount','-t','ext4','-o','loop,nodev,nosuid,noexec',str(image),str(data_mount)],check=True);inner=True
 missing={row['path'] for row in directories if not (data_mount/row['path']).exists()}
 assert missing=={row['path'] for row in directories if '/base/com.ohos.settingsdata' in row['path']}
 assert len(missing)==6
 before=fingerprint(data_mount,missing)
 for row in sorted(directories,key=lambda item:(len(Path(item['path']).parts),item['path'])):
  path=data_mount/row['path']
  assert path.resolve().is_relative_to(data_mount.resolve()) and not path.is_symlink() and not path.parent.is_symlink()
  if row['path'] in missing:
   path.mkdir(mode=0o700);os.chown(path,row['uid'],row['gid']);os.chmod(path,row['mode'])
   os.setxattr(path,'security.selinux',row['selinux'].encode()+b'\0')
  current=path.stat()
  assert (current.st_uid,current.st_gid,stat.S_IMODE(current.st_mode))==(row['uid'],row['gid'],row['mode'])
  assert os.getxattr(path,'security.selinux').rstrip(b'\0').decode()==row['selinux']
 after=fingerprint(data_mount,missing);assert before==after
 os.sync()
 subprocess.run(['umount',str(data_mount)],check=True);inner=False;data_mount.rmdir()
 check=subprocess.run(['e2fsck','-f','-n',str(image)],capture_output=True,text=True,timeout=180)
 assert check.returncode==0,check.stderr
 final=sha(image);assert final!=expected
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 assert image.stat().st_blocks*512>=8589934592
 result=dict(data_path='/mnt/lab/harmony-settings-data-197/data.ext4',candidate_before_sha256=expected,
  candidate_after_sha256=final,filesystem_uuid='b8383c4f-844b-46cc-9d67-34a3745b3f1f',
  directories_created=len(missing),existing_tree_before=before,existing_tree_after=after,
  source_directory_metadata='reports/settingsdata-scaffolding-216/plan.json',
  private_backup_path=str(backup),private_backup_bytes=backup.stat().st_size,backup_hash_verified=True,
  active165_sha256_verified_unchanged=True,offline_fsck_exit=0,original_images_modified=False,
  caller_or_token_records_modified=False,raw_app_state_exported=False,boot_selected=False,
  settings_ui_verified=False,usb_work_paused=True)
 (backup_root/'repair.json').open('x').write(json.dumps(result,indent=2))
 os.sync()
finally:
 if inner:subprocess.run(['umount',str(data_mount)],check=True);data_mount.rmdir()
 if outer:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
assert command(['efibootmgr','-v'])==firmware
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    source = json.loads((ROOT / 'reports/settingsdata-scaffolding-216/plan.json').read_text())
    original = json.loads((ROOT / 'reports/settingsdata-directories-214/source.json').read_text())
    mapping = {row['path']: row for row in original['directory_metadata']}
    for row in source['directories']:
        assert {key: row[key] for key in ['path', 'uid', 'gid', 'mode']} == mapping[row['path']]
        assert row['label_origin'] == 'original state-labels.tsv'
    helper = runpy.run_path(str(ROOT / 'next-experiment/prepare-settingsdata-scaffolding-215.py'))
    code = ('from pathlib import Path\nimport gzip,hashlib,json,os,shutil,stat,subprocess\n' +
        inspect.getsource(helper['sha']) + '\n' + inspect.getsource(helper['fingerprint']) + '\n' +
        'directories=' + repr(source['directories']) + '\nexpected=' + repr(EXPECTED) + '\n' + REMOTE)
    compile(code, 'settingsdata-repair231-remote', 'exec')
    REPORT.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=code,
        capture_output=True, text=True, timeout=1800)
    if result.stderr:
        (REPORT / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    (REPORT / 'result.json').open('x').write(result.stdout)
    print(result.stdout)
