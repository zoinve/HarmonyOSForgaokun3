"""Copy the inactive data filesystem through a read-only mount; never repair it."""
from pathlib import Path
import gzip
import hashlib
import json
import os
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/persistent-data-backup-169'
DEST = ROOT / 'artifacts/persistent-data-backup-169'
REMOTE = r'''
from pathlib import Path
import fcntl,gzip,hashlib,json,os,stat,subprocess,sys
device='/dev/nvme0n1p4'
target=Path('/mnt/harmony-persistent-backup169')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=30)
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098' and identity['TYPE']=='ext4'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert not target.exists()
target.mkdir(mode=0o700)
mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(target)],check=True,timeout=30)
 mounted=True
 path=target/'harmony-persistent-data-165/data.ext4'
 assert not command(['losetup','-j',str(path)]).strip()
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 with os.fdopen(fd,'rb') as source:
  fcntl.flock(source,fcntl.LOCK_SH|fcntl.LOCK_NB)
  before=os.fstat(source.fileno())
  assert stat.S_ISREG(before.st_mode) and before.st_size==8589934592 and before.st_nlink==1
  assert before.st_uid==0 and stat.S_IMODE(before.st_mode)==0o600
  source.seek(1024)
  header=source.read(120)
  assert header[56:58]==b'\x53\xef' and header[104:120].hex()=='eaa446cbb02a494f8a5ea02c8516cbc7'
  source.seek(0)
  digest=hashlib.sha256()
  copied=0
  with gzip.GzipFile(fileobj=sys.stdout.buffer,mode='wb',compresslevel=1,mtime=0) as output:
   while True:
    chunk=source.read(4*1024*1024)
    if not chunk:break
    copied+=len(chunk)
    digest.update(chunk)
    output.write(chunk)
  sys.stdout.buffer.flush()
  after=os.fstat(source.fileno())
  fields=['st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns']
  assert all(getattr(before,name)==getattr(after,name) for name in fields)
  assert copied==8589934592
  result=dict(source_readonly=True,journal_replayed=False,source_bytes=copied,
   source_sha256=digest.hexdigest(),source_identity_unchanged=True,repair_attempted=False)
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True,timeout=60)
 target.rmdir()
result['lab_partition_unmounted']=True
sys.stderr.write(json.dumps(result)+'\n')
'''

if __name__ == '__main__':
    assert not REPORT.exists() and not DEST.exists(), 'preserve numbered backup evidence'
    assert shutil.disk_usage(ROOT).free > 12 * 1024**3
    compile(REMOTE, 'persistent-data-backup169-remote', 'exec')
    runpy.run_path(str(BASE / 'commercial-workflow-166.py'))['configure_local_transport']()
    REPORT.mkdir()
    DEST.mkdir(parents=True, mode=0o700)
    archive = DEST / 'data.ext4.gz'
    with archive.open('xb') as output, (REPORT / 'transport.stderr').open('x') as errors:
        os.chmod(archive, 0o600)
        proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'HostKeyAlias=192.168.10.128', '-o', 'ServerAliveInterval=15',
            'zoinve@192.168.10.128', 'sudo -n python3 -'],
            input=REMOTE.encode(), stdout=output, stderr=errors, timeout=1200)
        output.flush()
        os.fsync(output.fileno())
    assert proc.returncode == 0, 'backup failed; retain partial archive and transport evidence'
    result = json.loads((REPORT / 'transport.stderr').read_text())
    print('Transfer complete; checking decompressed full-image hash.', flush=True)
    digest = hashlib.sha256()
    size = 0
    with gzip.open(archive, 'rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    assert size == result['source_bytes'] and digest.hexdigest() == result['source_sha256']
    with archive.open('rb') as stream:
        compressed_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    result.update(backup_path=str(archive.relative_to(ROOT)), compressed_bytes=archive.stat().st_size,
        compressed_sha256=compressed_sha, decompressed_hash_verified=True,
        original_source_modified=False, user_file_contents_exported_to_logs=False)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
