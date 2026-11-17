'''Transfer and stage an isolated data candidate; never replace active165.'''
from pathlib import Path
import json
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / 'reports/settings-data-deploy-198'
SSH = ['ssh', '-i', 'C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
       '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'HostKeyAlias=192.168.10.128', '-o', 'ConnectTimeout=8',
       'zoinve@192.168.10.128']
HASH = 'f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce'
TRANSFER = r'''
from pathlib import Path
import gzip,hashlib,json,os,shutil,sys
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/settings-data-transfer-198')
assert os.geteuid()==0 and not root.exists()
assert shutil.disk_usage(root.parent).free>16*1024**3
root.mkdir(mode=0o700)
digest=hashlib.sha256();total=0
with gzip.GzipFile(fileobj=sys.stdin.buffer) as source,(root/'data.ext4').open('xb') as dest:
 os.fchmod(dest.fileno(),0o600)
 while chunk:=source.read(1024**2):
  total+=len(chunk);assert total<=8589934592
  digest.update(chunk);dest.write(chunk)
 dest.flush();os.fsync(dest.fileno())
assert total==8589934592 and digest.hexdigest()==expected
result=dict(bytes=total,sha256=digest.hexdigest(),private_staging=True,target_lab_modified=False)
(root/'transfer.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
'''
DEPLOY = r'''
from pathlib import Path
import hashlib,json,os,shutil,stat,subprocess
device='/dev/nvme0n1p4';target=Path('/mnt/settings-data-deploy-198')
source=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/settings-data-transfer-198/data.ext4')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert os.geteuid()==0 and not target.exists()
assert source.stat().st_size==8589934592 and not source.is_symlink() and sha(source)==expected
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['TYPE']=='ext4' and identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
firmware=command(['efibootmgr','-v'])
target.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(target)],check=True,timeout=30);mounted=True
 assert target.stat().st_dev==os.stat(device).st_rdev
 assert shutil.disk_usage(target).free>16*1024**3
 active=target/'harmony-persistent-data-165/data.ext4'
 assert active.is_file() and not active.is_symlink() and active.stat().st_size==8589934592
 assert not command(['losetup','-j',str(active)]).strip()
 active_before=sha(active)
 root=target/'harmony-settings-data-197'
 assert not root.exists() and not root.is_symlink()
 root.mkdir(mode=0o700)
 data=root/'data.ext4'
 with source.open('rb') as src,data.open('xb') as out:
  os.fchmod(out.fileno(),0o600);os.posix_fallocate(out.fileno(),0,8589934592)
  shutil.copyfileobj(src,out,1024**2);out.flush();os.fsync(out.fileno())
 assert sha(data)==expected
 info=data.stat()
 assert info.st_uid==0 and info.st_gid==0 and info.st_nlink==1
 assert stat.S_IMODE(info.st_mode)==0o600 and info.st_blocks*512>=8589934592
 probe=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',str(data)]).splitlines() if '=' in line)
 assert probe['TYPE']=='ext4' and probe['UUID']=='b8383c4f-844b-46cc-9d67-34a3745b3f1f'
 check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,text=True,timeout=180)
 assert check.returncode==0,check.stderr
 active_after=sha(active);assert active_after==active_before
 result=dict(data_path='/mnt/lab/harmony-settings-data-197/data.ext4',filesystem_uuid=probe['UUID'],
  candidate_sha256=expected,capacity_bytes=info.st_size,allocated_bytes=info.st_blocks*512,
  offline_fsck_exit=check.returncode,active165_before_sha256=active_before,active165_after_sha256=active_after,
  active165_unchanged=True,original_images_modified=False,boot_selected=False,usb_work_paused=True)
 with (root/'provision.json').open('x') as f:json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(root/'provision.json',0o400);os.sync()
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True,timeout=60)
 target.rmdir()
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert command(['efibootmgr','-v'])==firmware
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


def main():
    assert not REPORT.exists(), 'preserve numbered transfer evidence'
    REPORT.mkdir()
    code = 'expected=' + repr(HASH) + '\n' + TRANSFER
    compile(code, 'transfer198', 'exec')
    with (REPORT / 'compress.stderr').open('wb') as errors:
        compressor = subprocess.Popen(['wsl', '-d', 'Debian', '--', 'gzip', '-1', '-c',
            '/home/zoinve/harmony-virgl-883/settings-data-candidate-191-r2/data.ext4'],
            stdout=subprocess.PIPE, stderr=errors)
        try:
            result = subprocess.run(SSH + ['sudo -n python3 -c ' + shlex.quote(code)],
                stdin=compressor.stdout, capture_output=True, timeout=1800)
        finally:
            compressor.stdout.close()
            if compressor.poll() is None:
                compressor.terminate()
            compressor.wait(timeout=30)
    for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        (REPORT / ('transfer.' + suffix)).open('xb').write(data)
    assert result.returncode == 0 and compressor.returncode == 0, result.stderr.decode(errors='replace')
    transfer = json.loads(result.stdout)
    (REPORT / 'transfer.json').open('x').write(json.dumps(transfer,indent=2))
    print('Private transfer verified; staging isolated LAB candidate.',flush=True)
    code = 'expected=' + repr(HASH) + '\n' + DEPLOY
    compile(code, 'deploy198', 'exec')
    result = subprocess.run(SSH + ['sudo -n python3 -'], input=code,text=True,capture_output=True,timeout=900)
    for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        (REPORT / ('deploy.' + suffix)).open('x').write(data)
    assert result.returncode == 0,result.stderr
    (REPORT / 'provision.json').open('x').write(json.dumps(json.loads(result.stdout),indent=2))
    print(result.stdout)


if __name__ == '__main__':
    main()
