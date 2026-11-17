"""Stream local 216 to a fresh LAB path, avoiding Ubuntu staging space."""
from pathlib import Path
import json
import runpy
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settingsdata-deploy-218'
REMOTE = r'''
from pathlib import Path
import gzip,hashlib,json,os,shutil,stat,subprocess,sys
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
device='/dev/nvme0n1p4';mount=Path('/mnt/settingsdata-deploy-218')
assert os.geteuid()==0 and not mount.exists()
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
firmware=command(['efibootmgr','-v'])
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 assert shutil.disk_usage(mount).free>8589934592+1073741824
 active=mount/'harmony-persistent-data-165/data.ext4'
 previous=mount/'harmony-settings-data-197/data.ext4'
 for image in [active,previous]:
  assert image.is_file() and not image.is_symlink() and not image.parent.is_symlink()
  assert image.stat().st_size==8589934592 and not command(['losetup','-j',str(image)]).strip()
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 assert sha(previous)=='c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42'
 root=mount/'harmony-settings-data-216'
 assert not root.exists() and not root.is_symlink()
 root.mkdir(mode=0o700);data=root/'data.ext4'
 digest=hashlib.sha256();total=0
 with gzip.GzipFile(fileobj=sys.stdin.buffer) as source,data.open('xb') as dest:
  os.fchmod(dest.fileno(),0o600);os.posix_fallocate(dest.fileno(),0,8589934592)
  while chunk:=source.read(1024**2):
   total+=len(chunk);assert total<=8589934592
   digest.update(chunk);dest.write(chunk)
  dest.flush();os.fsync(dest.fileno())
 assert total==8589934592 and digest.hexdigest()==expected
 assert sha(data)==expected
 info=data.stat()
 assert stat.S_IMODE(info.st_mode)==0o600 and info.st_uid==0 and info.st_gid==0 and info.st_nlink==1
 assert info.st_blocks*512>=8589934592
 assert command(['blkid','-p','-s','UUID','-o','value',str(data)]).strip()==identity
 check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,text=True,timeout=180)
 assert check.returncode==0,check.stderr
 assert sha(active)=='36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce'
 assert sha(previous)=='c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42'
 result=dict(data_path='/mnt/lab/harmony-settings-data-216/data.ext4',candidate_sha256=expected,
  filesystem_uuid=identity,capacity_bytes=info.st_size,allocated_bytes=info.st_blocks*512,
  active165_unchanged=True,previous_candidate197_unchanged=True,offline_fsck_exit=0,
  ubuntu_staging_image_created=False,boot_selected=False,settings_ui_verified=False,usb_work_paused=True)
 with (root/'provision.json').open('x') as stream:
  json.dump(result,stream,indent=2);stream.flush();os.fsync(stream.fileno())
 os.chmod(root/'provision.json',0o400);os.sync()
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True,timeout=60)
 mount.rmdir()
assert command(['efibootmgr','-v'])==firmware
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    assert not REPORT.exists(), 'immutable evidence'
    source = json.loads((ROOT / 'reports/settingsdata-scaffolding-216/result.json').read_text())
    assert source['offline_fsck_status'] == 0 and source['existing_tree_before'] == source['existing_tree_after']
    assert source['source_unchanged'] and source['candidate_unmounted']
    code = 'expected=' + repr(source['candidate_sha256']) + '\nidentity=' + repr(source['candidate_uuid']) + '\n' + REMOTE
    compile(code, 'deploy218-remote', 'exec')
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    REPORT.mkdir()
    with (REPORT / 'compress.stderr').open('xb') as errors:
        compressor = subprocess.Popen(['wsl', '-d', 'Debian', '-u', 'root', '--',
            'gzip', '-1', '-c', source['candidate_path']], stdout=subprocess.PIPE, stderr=errors)
        try:
            result = subprocess.run(ssh + ['sudo -n python3 -c ' + shlex.quote(code)],
                stdin=compressor.stdout, capture_output=True, timeout=1800)
        finally:
            compressor.stdout.close()
            if compressor.poll() is None:
                compressor.terminate()
            compressor.wait(timeout=30)
    for suffix, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (REPORT / ('deploy.' + suffix)).open('xb').write(data)
    assert result.returncode == 0 and compressor.returncode == 0, result.stderr.decode(errors='replace')
    record = json.loads(result.stdout)
    (REPORT / 'provision.json').open('x').write(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))
