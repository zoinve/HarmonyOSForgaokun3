"""Inspect the unmounted outer LAB filesystem without journal replay or repair."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/lab-ext4-inspection-170'
REMOTE = r'''
import json,os,subprocess
device='/dev/nvme0n1p4'
env=dict(os.environ,LC_ALL='C')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=30,env=env)
identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098' and identity['TYPE']=='ext4'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
header=command(['dumpe2fs','-h',device])
check=subprocess.run(['e2fsck','-f','-n',device],capture_output=True,text=True,timeout=300,env=env)
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
print(json.dumps(dict(partition_uuid=identity['UUID'],read_only=True,repair_attempted=False,
 partition_unmounted=True,fsck_exit=check.returncode,fsck_stdout=check.stdout,
 fsck_stderr=check.stderr,filesystem_header=header),indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists(), 'preserve numbered inspection'
    assert json.loads((BASE.parent / 'reports/persistent-data-backup-169/result.json').read_text())['decompressed_hash_verified']
    compile(REMOTE, 'lab-ext4-inspection170-remote', 'exec')
    runpy.run_path(str(BASE / 'commercial-workflow-166.py'))['configure_local_transport']()
    REPORT.mkdir()
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'HostKeyAlias=192.168.10.128', 'zoinve@192.168.10.128', 'sudo -n python3 -'],
        input=REMOTE, capture_output=True, text=True, timeout=360)
    (REPORT / 'transport.stderr').open('x').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({name: result[name] for name in ['partition_uuid', 'read_only',
        'repair_attempted', 'partition_unmounted', 'fsck_exit']}, indent=2))
