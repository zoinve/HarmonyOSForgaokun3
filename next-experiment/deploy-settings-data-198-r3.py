'''Keep failed evidence bytes while reclaiming zero extents before the real transfer.'''
from pathlib import Path
import json
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REMOTE=r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/settings198-sparse')
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not mount.exists()
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert subprocess.check_output(['blkid','-p','-o','value','-s','UUID',device],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 data=mount/'harmony-settings-data-197-incomplete-198-r1/data.ext4'
 assert data.is_file() and not data.is_symlink() and not data.parent.is_symlink()
 assert data.resolve().parent.parent==mount.resolve() and data.stat().st_size==8589934592
 assert not subprocess.check_output(['losetup','-j',str(data)],text=True).strip()
 zero=hashlib.sha256();chunk=bytes(1024**2)
 for _ in range(8192):zero.update(chunk)
 before=sha(data);assert before==zero.hexdigest(),'only the known all-zero failed transfer may be sparsified'
 allocated_before=data.stat().st_blocks*512
 subprocess.run(['fallocate','--dig-holes',str(data)],check=True,timeout=180)
 after=sha(data);assert after==before and data.stat().st_size==8589934592
 os.sync()
 result=dict(failed_candidate_bytes_unchanged=True,sha256=after,
  allocated_before=allocated_before,allocated_after=data.stat().st_blocks*512,
  free_bytes=shutil.disk_usage(mount).free,active165_modified=False)
 assert result['free_bytes']>16*1024**3
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
print(json.dumps(result))
'''


if __name__=='__main__':
    report=ROOT/'reports/settings-data-sparse-198-r1'
    assert not report.exists();report.mkdir()
    old=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))
    result=subprocess.run(old['SSH']+['sudo -n python3 -'],input=REMOTE,text=True,capture_output=True,timeout=300)
    for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        (report/('preserve.'+suffix)).open('x').write(data)
    assert result.returncode==0,result.stderr
    (report/'result.json').open('x').write(json.dumps(json.loads(result.stdout),indent=2))
    runpy.run_path(str(BASE/'deploy-settings-data-198-r1.py'))['main'](ROOT/'reports/settings-data-deploy-198-r3')
