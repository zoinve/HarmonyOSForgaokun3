"""Preserve read-only consistency diagnostics after the failed 168 verifier."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-168'
REMOTE = r'''
from pathlib import Path
import json, subprocess
device='/dev/nvme0n1p4'
target=Path('/mnt/harmony-persistent-fsck-inspect168')
def command(args):
 return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=120)
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert not target.exists()
target.mkdir(mode=0o700)
mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(target)],check=True,timeout=30)
 mounted=True
 data=target/'harmony-persistent-data-165/data.ext4'
 assert data.is_file() and not data.is_symlink() and data.stat().st_size==8589934592
 assert not command(['losetup','-j',str(data)]).strip()
 inner=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',str(data)]).splitlines() if '=' in line)
 assert inner['UUID']=='eaa446cb-b02a-494f-8a5e-a02c8516cbc7'
 check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,text=True,timeout=120)
 header=command(['dumpe2fs','-h',str(data)])
 result=dict(read_only=True,repair_attempted=False,filesystem_uuid=inner['UUID'],
  fsck_exit=check.returncode,fsck_stdout=check.stdout,fsck_stderr=check.stderr,filesystem_header=header)
finally:
 if mounted:subprocess.run(['umount',str(target)],check=True,timeout=60)
 target.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    output = REPORT / 'persistent-fsck-inspection.json'
    assert not output.exists()
    assert (REPORT / 'persistent-offline-verification.stderr').is_file()
    compile(REMOTE, 'persistent-fsck-inspection168-remote', 'exec')
    runpy.run_path(str(BASE / 'commercial-workflow-166.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'HostKeyAlias=192.168.10.128', 'zoinve@192.168.10.128', 'sudo -n python3 -'],
        input=REMOTE, text=True, capture_output=True, timeout=240)
    (REPORT / 'persistent-fsck-inspection.stderr').open('x').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
