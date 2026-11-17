"""Apply the copy-tested repair to an inactive, backed-up data image only."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/persistent-source-recovery-171'
REMOTE = r'''
from pathlib import Path
import fcntl,hashlib,json,os,re,stat,subprocess
env=dict(os.environ,LC_ALL='C')
device='/dev/nvme0n1p4'
target=Path('/mnt/harmony-persistent-recovery171')
def command(args,limit=120):
 return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=limit,env=env)
def check(path,mode):
 p=subprocess.run(['e2fsck','-f',mode,str(path)],capture_output=True,text=True,timeout=180,env=env)
 return dict(exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098' and identity['TYPE']=='ext4'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert not target.exists()
target.mkdir(mode=0o700)
mounted=False
result=dict(backup_verified=True,original_system_images_modified=False,native_boot_performed=False)
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(target)],check=True,timeout=30)
 mounted=True
 data=target/'harmony-persistent-data-165/data.ext4'
 assert not command(['losetup','-j',str(data)]).strip()
 with os.fdopen(os.open(data,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC),'rb') as stream:
  before=os.fstat(stream.fileno())
  assert stat.S_ISREG(before.st_mode) and before.st_size==8589934592 and before.st_nlink==1
  assert before.st_uid==0 and stat.S_IMODE(before.st_mode)==0o600
  digest=hashlib.file_digest(stream,'sha256').hexdigest()
 assert digest==expected_sha,'source changed since verified backup; no repair'
 result['source_before_sha256']=digest
 baseline=check(data,'-n')
 assert baseline['exit']==4
 actual=[int(value) for value in re.findall(r'Inode (\d+) was part of the orphaned inode list',baseline['stdout'])]
 assert actual==expected_orphans and actual,'unexpected errors; no repair'
 result['baseline_readonly_fsck']=baseline
 subprocess.run(['umount',str(target)],check=True,timeout=60)
 mounted=False
 subprocess.run(['mount','-t','ext4','-o','rw,nodev,nosuid,noexec',device,str(target)],check=True,timeout=30)
 mounted=True
 with os.fdopen(os.open(data,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC),'r+b') as stream:
  fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
  current=os.fstat(stream.fileno())
  assert (current.st_dev,current.st_ino,current.st_size)==(before.st_dev,before.st_ino,before.st_size)
  assert hashlib.file_digest(stream,'sha256').hexdigest()==expected_sha
  assert not command(['losetup','-j',str(data)]).strip()
  repair=check(data,'-y')
  result['offline_repair']=repair
  assert repair['exit'] in [0,1],repair
  os.fsync(stream.fileno())
  after=check(data,'-n')
  result['post_repair_readonly_fsck']=after
  assert after['exit']==0,after
  header=command(['dumpe2fs','-h',str(data)])
  fields=dict(line.split(':',1) for line in header.splitlines() if ':' in line)
  assert fields['Filesystem UUID'].strip()=='eaa446cb-b02a-494f-8a5e-a02c8516cbc7'
  assert fields['Filesystem state'].strip()=='clean'
  marker=command(['debugfs','-R','cat /.harmony-persistent166/last-boot',str(data)]).strip()
  assert marker=='4294d07e-b415-4edb-b707-cd05bde7fa49'
  scene=command(['debugfs','-R','stat /app/el1/bundle/public/com.ohos.sceneboard',str(data)])
  assert 'Inode:' in scene and 'Type: directory' in scene
  stream.seek(0)
  result.update(source_after_sha256=hashlib.file_digest(stream,'sha256').hexdigest(),
   filesystem_clean=True,native_boot_marker_retained=True,sceneboard_install_directory_retained=True,
   application_databases_reset=False,source_capacity_bytes=current.st_size,
   repaired_orphan_inode_count=len(actual))
 subprocess.run(['sync','-f',str(data)],check=True,timeout=60)
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True,timeout=60)
 target.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists(), 'preserve numbered repair evidence'
    backup = json.loads((ROOT / 'reports/persistent-data-backup-169/result.json').read_text())
    trial = json.loads((ROOT / 'reports/persistent-recovery-170/result.json').read_text())
    outer = json.loads((ROOT / 'reports/lab-ext4-inspection-170/result.json').read_text())
    assert backup['decompressed_hash_verified'] and trial['copy_recovered_cleanly']
    assert trial['backup_archive_unchanged'] and outer['fsck_exit'] == 0
    archive = ROOT / backup['backup_path']
    with archive.open('rb') as stream:
        assert hashlib.file_digest(stream,'sha256').hexdigest() == backup['compressed_sha256']
    text = (ROOT / 'reports/persistent-recovery-170/before-readonly.stdout').read_text()
    orphans = [int(value) for value in re.findall(r'Inode (\d+) was part of the orphaned inode list',text)]
    assert orphans
    source = 'expected_sha=' + repr(backup['source_sha256']) + '\nexpected_orphans=' + repr(orphans) + '\n' + REMOTE
    compile(source,'persistent-source-recovery171-remote','exec')
    runpy.run_path(str(BASE / 'commercial-workflow-166.py'))['configure_local_transport']()
    REPORT.mkdir()
    proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostKeyAlias=192.168.10.128','zoinve@192.168.10.128','sudo -n python3 -'],
        input=source,capture_output=True,text=True,timeout=600)
    (REPORT / 'transport.stdout').open('x').write(proc.stdout)
    (REPORT / 'transport.stderr').open('x').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    (REPORT / 'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps({key:value for key,value in result.items() if not isinstance(value,dict)},indent=2))
