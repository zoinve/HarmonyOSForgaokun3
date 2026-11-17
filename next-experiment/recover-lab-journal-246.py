"""Replay only the outer LAB journal after a successful metadata-only trial."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/lab-journal-recovery-246'
REMOTE = r'''
from pathlib import Path
import hashlib,json,os,re,stat,subprocess
os.environ['LC_ALL']='C';os.umask(0o077)
device='/dev/nvme0n1p4'
parent=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')
work=parent/'lab-journal-recovery-246'
mount=Path('/mnt/lab-journal-verification-246')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=300)
def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def unmounted():
 assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
def metadata(path):
 text=command(['debugfs','-R','stat '+path,device])
 assert 'Inode:' in text and 'EXTENTS:' in text
 rows=[line for line in text.splitlines() if not re.match(r'\s*(?:[acm]time:|crtime:|Inode checksum:|Generation:)',line)]
 return hashlib.sha256(('\n'.join(rows)+'\n').encode()).hexdigest()
def measure():
 assert not mount.exists();unmounted();mount.mkdir(mode=0o700);mounted=False
 try:
  subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
  assert mount.stat().st_dev==os.stat(device).st_rdev
  values={}
  for key,relative in [('active165','harmony-persistent-data-165/data.ext4'),('candidate197','harmony-settings-data-197/data.ext4')]:
   path=mount/relative
   assert path.is_file() and not path.is_symlink() and not path.parent.is_symlink()
   assert path.stat().st_size==8589934592 and stat.S_IMODE(path.stat().st_mode)==0o600
   assert path.stat().st_uid==path.stat().st_gid==0
   assert not command(['losetup','-j',str(path)]).strip()
   values[key]=sha(path)
  return values
 finally:
  if mounted:subprocess.run(['umount',str(mount)],check=True,timeout=60)
  mount.rmdir()
assert os.geteuid()==0 and not work.exists()
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
unmounted()
trial=json.loads((parent/'lab-recovery-245/result.json').read_text())
assert trial==expected_trial and trial['trial_clean_and_protected']
assert trial['journal_only_exit'] in [0,1] and trial['preen_exit'] is None
backup=Path(trial['metadata_backup_path'])
assert backup.parent==parent/'lab-recovery-245' and not backup.is_symlink()
assert sha(backup)==trial['metadata_backup_sha256']
protected={key:metadata(key) for key in trial['protected_metadata_before']}
assert protected==trial['protected_metadata_before']
before=measure()
assert before==expected_hashes
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
firmware=command(['efibootmgr','-v'])
work.mkdir(mode=0o700)
undo=work/'outer-journal.e2undo'
recovery=subprocess.run(['e2fsck','-p','-E','journal_only','-z',str(undo),device],capture_output=True,text=True,timeout=300)
with (work/'journal-result.json').open('x') as stream:
 json.dump(dict(exit_status=recovery.returncode,stdout=recovery.stdout,stderr=recovery.stderr),stream,indent=2)
assert recovery.returncode in [0,1],recovery.stdout+recovery.stderr
check=subprocess.run(['e2fsck','-f','-n',device],capture_output=True,text=True,timeout=300)
with (work/'readonly-result.json').open('x') as stream:
 json.dump(dict(exit_status=check.returncode,stdout=check.stdout,stderr=check.stderr),stream,indent=2)
assert check.returncode==0,check.stdout+check.stderr
after=measure();assert after==before
assert {key:metadata(key) for key in protected}==protected
assert sha(backup)==trial['metadata_backup_sha256']
assert undo.is_file() and not undo.is_symlink();undo.chmod(0o600)
with undo.open('rb') as stream:os.fsync(stream.fileno())
assert command(['efibootmgr','-v'])==firmware
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
unmounted()
result=dict(journal_only_exit=recovery.returncode,outer_readonly_fsck_exit=check.returncode,
 real_device_journal_replayed=True,manual_fsck_repair_requested=False,
 protected_content_hashes_before=before,protected_content_hashes_after=after,
 active165_and_candidate197_content_unchanged=True,protected_metadata_unchanged=True,
 verified_metadata_backup_retained=True,undo_path=str(undo),undo_bytes=undo.stat().st_size,
 undo_sha256=sha(undo),lab_partition_unmounted=True,ubuntu_default_preserved=True,
 firmware_unchanged=True,screenoff_timer_enabled_active=True,
 inner_candidate_fsck_clean_not_yet_verified=True,settings_ui_verified=False,boot_requested=False)
with (work/'result.json').open('x') as stream:json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    trial = json.loads((ROOT / 'reports/lab-recovery-trial-245/result.json').read_text())
    previous = json.loads((ROOT / 'reports/settings-storage-inspection-244.json').read_text())
    expected = dict(active165=previous['active165_sha256'], candidate197=previous['candidate_sha256'])
    code = 'expected_trial=' + repr(trial) + '\nexpected_hashes=' + repr(expected) + '\n' + REMOTE
    REPORT.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    proc = subprocess.run(ssh + ['sudo -n python3 -'], input=code, capture_output=True,
                          text=True, timeout=1500)
    if proc.stderr:
        (REPORT / 'stderr').open('x').write(proc.stderr)
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout)
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
