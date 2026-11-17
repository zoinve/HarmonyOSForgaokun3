"""Exercise recovery on sparse metadata only; never write the real LAB device."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/lab-recovery-trial-245'
REMOTE = r'''
from pathlib import Path
import hashlib,json,os,re,shutil,stat,subprocess
os.environ['LC_ALL']='C'
device='/dev/nvme0n1p4'
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/lab-recovery-245')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=300)
def sha(path):
 with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def unmounted():
 assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
def metadata(path,filesystem):
 text=command(['debugfs','-R','stat '+path,str(filesystem)])
 assert 'Inode:' in text and 'EXTENTS:' in text
 rows=[line for line in text.splitlines() if not re.match(r'\s*(?:[acm]time:|crtime:|Inode checksum:|Generation:)',line)]
 return hashlib.sha256(('\n'.join(rows)+'\n').encode()).hexdigest()
def run(args,name):
 proc=subprocess.run(args,capture_output=True,text=True,timeout=300)
 record=dict(exit_status=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
 path=work/(name+'.json')
 with path.open('x') as stream:json.dump(record,stream,indent=2)
 path.chmod(0o600)
 return record
def flush(path):
 with path.open('rb') as stream:os.fsync(stream.fileno())
assert os.geteuid()==0 and not work.exists()
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert os.stat(device).st_mode & stat.S_IFBLK
unmounted()
assert shutil.disk_usage(work.parent).free>8*1024**3
assert command(['uname','-r']).strip()=='7.1.0-rc3-gaokun3+'
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
firmware=command(['efibootmgr','-v'])
os.umask(0o077);work.mkdir(mode=0o700)
protected=['/harmony-persistent-data-165/data.ext4','/harmony-settings-data-197/data.ext4']
before={path:metadata(path,device) for path in protected}
backup=work/'lab-before.qcow2';trial=work/'lab-trial.raw'
assert run(['e2image','-Q',device,str(backup)],'metadata-backup')['exit_status']==0
backup.chmod(0o600);flush(backup)
backup_hash=sha(backup)
assert backup.stat().st_blocks*512<2*1024**3
assert run(['e2image','-r',str(backup),str(trial)],'trial-conversion')['exit_status']==0
trial.chmod(0o600);flush(trial)
assert trial.stat().st_size==int(command(['blockdev','--getsize64',device]))
assert trial.stat().st_blocks*512<2*1024**3
assert {path:metadata(path,trial) for path in protected}==before
journal=run(['e2fsck','-p','-E','journal_only','-z',str(work/'journal-trial.e2undo'),str(trial)],'trial-journal')
check=run(['e2fsck','-f','-n',str(trial)],'trial-after-journal')
preen=None
if check['exit_status']!=0 and journal['exit_status'] in [0,1]:
 preen=run(['e2fsck','-f','-p','-z',str(work/'preen-trial.e2undo'),str(trial)],'trial-preen')
 check=run(['e2fsck','-f','-n',str(trial)],'trial-final-readonly')
after={path:metadata(path,trial) for path in protected}
assert {path:metadata(path,device) for path in protected}==before
assert sha(backup)==backup_hash
unmounted()
assert command(['efibootmgr','-v'])==firmware
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
result=dict(source_device=device,source_written=False,lab_partition_unmounted=True,
 metadata_backup_path=str(backup),metadata_backup_sha256=backup_hash,
 metadata_backup_bytes=backup.stat().st_size,metadata_backup_allocated_bytes=backup.stat().st_blocks*512,
 trial_apparent_bytes=trial.stat().st_size,trial_allocated_bytes=trial.stat().st_blocks*512,
 journal_only_exit=journal['exit_status'],preen_exit=preen['exit_status'] if preen else None,
 final_trial_readonly_fsck_exit=check['exit_status'],protected_metadata_before=before,
 protected_metadata_after=after,protected_metadata_unchanged=before==after,
 trial_clean_and_protected=check['exit_status']==0 and before==after,
 full_file_data_copied=False,actual_file_contents_not_proven_by_metadata_trial=True,
 ubuntu_default_preserved=True,firmware_unchanged=True,screenoff_timer_enabled_active=True,
 real_device_recovery_attempted=False,boot_requested=False)
with (work/'result.json').open('x') as stream:json.dump(result,stream,indent=2)
flush(work/'result.json')
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    previous = json.loads((ROOT / 'reports/settings-storage-inspection-244.json').read_text())
    assert previous['active165_unchanged'] and previous['lab_partition_unmounted']
    REPORT.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    proc = subprocess.run(ssh + ['sudo -n python3 -'], input=REMOTE,
                          capture_output=True, text=True, timeout=1500)
    if proc.stderr:
        (REPORT / 'stderr').open('x').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
