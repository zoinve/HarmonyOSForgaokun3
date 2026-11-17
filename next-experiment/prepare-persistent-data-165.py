"""Provision a new dedicated data file on the identity-checked LAB filesystem."""
from pathlib import Path
import json
import runpy
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/persistent-data-165'
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,os,shutil,stat,subprocess
device='/dev/nvme0n1p4'
target=Path('/mnt/harmony-data165')
seed=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/oobe-seed-123/seed.ext4')
seed_hash='02c810f94799cf4b89cc59dea2409981b4678e8b201d60c0ceb62fd7397b21cd'
capacity=8*1024**3
def command(args):return subprocess.check_output(args,text=True,timeout=120)
def digest(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def fresh(path,data):
 with path.open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
assert os.geteuid()==0
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098' and identity['TYPE']=='ext4'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert not target.exists(), 'preserve an existing mountpoint instead of reusing it'
assert not seed.is_symlink() and seed.stat().st_size==536870912 and digest(seed)==seed_hash
status=command(['bootctl','status','--no-pager'])
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
firmware=command(['efibootmgr','-v'])
target.mkdir(mode=0o700)
mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec'+('' if apply else ',ro,noload'),device,str(target)],check=True,timeout=30)
 mounted=True
 assert target.stat().st_dev==os.stat(device).st_rdev
 free=shutil.disk_usage(target).free
 root=target/'harmony-persistent-data-165'
 assert not root.exists() and not root.is_symlink()
 result=dict(apply=apply,partition=device,partition_uuid=identity['UUID'],free_bytes_before=free,
  data_path='/mnt/lab/harmony-persistent-data-165/data.ext4',capacity_bytes=capacity,
  seed_sha256=seed_hash,partition_table_changed=False,original_images_modified=False,boot_selected=False)
 assert free>capacity+8*1024**3, 'retain at least 8 GiB for evidence and filesystem headroom'
 if apply:
  root.mkdir(mode=0o700)
  data=root/'data.ext4'
  with seed.open('rb') as source,data.open('xb') as dest:
   os.fchmod(dest.fileno(),0o600)
   shutil.copyfileobj(source,dest,1024**2)
   dest.flush();os.fsync(dest.fileno())
  assert digest(data)==seed_hash
  subprocess.run(['fallocate','-l',str(capacity),str(data)],check=True,timeout=120)
  subprocess.run(['e2fsck','-f','-p',str(data)],check=True,capture_output=True,timeout=120)
  subprocess.run(['resize2fs',str(data)],check=True,capture_output=True,timeout=120)
  check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,text=True,timeout=120)
  assert check.returncode==0,check.stderr
  probe=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',str(data)]).splitlines() if '=' in line)
  assert probe['TYPE']=='ext4'
  st=data.stat()
  assert st.st_size==capacity and st.st_blocks*512>=capacity and stat.S_IMODE(st.st_mode)==0o600
  result.update(filesystem_uuid=probe['UUID'],initial_data_sha256=digest(data),allocated_bytes=st.st_blocks*512,
   free_bytes_after=shutil.disk_usage(target).free,offline_fsck_clean=True,seed_unchanged=digest(seed)==seed_hash)
  assert result['seed_unchanged'] and result['free_bytes_after']>8*1024**3
  fresh(root/'provision.json',json.dumps(result,indent=2).encode())
  os.chmod(root/'provision.json',0o400)
  fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
  os.sync()
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True,timeout=60)
 target.rmdir()
assert command(['efibootmgr','-v'])==firmware
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert sys.argv[1:] in [[], ['--apply']]
    apply = bool(sys.argv[1:])
    REPORT.mkdir(exist_ok=True)
    stem = 'provision' if apply else 'plan'
    assert not (REPORT / (stem + '.stdout')).exists(), 'preserve evidence'
    script = 'apply=' + repr(apply) + '\n' + PAYLOAD
    compile(script, 'persistent-data165-remote', 'exec')
    runpy.run_path(str(BASE / 'commercial-workflow-164.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=192.168.10.128','-o','ConnectTimeout=8','zoinve@192.168.10.128',
        'sudo -n python3 -'],input=script,text=True,capture_output=True,timeout=600)
    for suffix, text in [('stdout',proc.stdout),('stderr',proc.stderr)]:
        (REPORT / (stem + '.' + suffix)).open('x').write(text)
    assert proc.returncode == 0, proc.stderr
    result=json.loads(proc.stdout)
    (REPORT / (stem + '.json')).open('x').write(json.dumps(result,indent=2))
    print(proc.stdout)
