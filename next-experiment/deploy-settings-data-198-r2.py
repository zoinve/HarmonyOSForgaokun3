'''Preserve the incomplete transfer, then read the private source as WSL root.'''
from pathlib import Path
import json
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REMOTE=r'''
from pathlib import Path
import json,os,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/settings198-preserve')
assert not mount.exists()
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
probe=subprocess.check_output(['blkid','-p','-o','value','-s','UUID',device],text=True).strip()
assert probe=='00029cdd-1748-4d2f-b73b-8e8164922098'
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 source=mount/'harmony-settings-data-197';dest=mount/'harmony-settings-data-197-incomplete-198-r1'
 assert source.is_dir() and not source.is_symlink() and source.resolve().parent==mount.resolve()
 assert not dest.exists() and dest.resolve().parent==mount.resolve()
 assert sorted(p.name for p in source.iterdir())==['data.ext4'] and not (source/'provision.json').exists()
 data=source/'data.ext4'
 assert not data.is_symlink() and data.stat().st_size==8589934592
 assert not subprocess.check_output(['losetup','-j',str(data)],text=True).strip()
 source.rename(dest);os.sync()
 result=dict(incomplete_candidate_preserved=dest.name,bytes=8589934592,
  reason='local_private_source_permission_denied_before_any_stream_bytes',active165_modified=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True)
 mount.rmdir()
print(json.dumps(result))
'''


if __name__=='__main__':
    report=ROOT/'reports/settings-data-preserve-198-r1'
    assert not report.exists();report.mkdir()
    old=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))
    result=subprocess.run(old['SSH']+['sudo -n python3 -'],input=REMOTE,text=True,capture_output=True,timeout=120)
    for suffix,data in [('stdout',result.stdout),('stderr',result.stderr)]:
        (report/('preserve.'+suffix)).open('x').write(data)
    assert result.returncode==0,result.stderr
    (report/'result.json').open('x').write(json.dumps(json.loads(result.stdout),indent=2))
    runpy.run_path(str(BASE/'deploy-settings-data-198-r1.py'))['main'](ROOT/'reports/settings-data-deploy-198-r2')
