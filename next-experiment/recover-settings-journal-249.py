"""Replay the candidate journal with verified metadata backup and full tree guards."""
from pathlib import Path
import inspect
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settings-journal-recovery-249'
REMOTE = r'''
os.environ['LC_ALL']='C';os.umask(0o077)
device='/dev/nvme0n1p4'
parent=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')
work=parent/'settings-journal-recovery-249'
outer=Path('/mnt/settings-journal-recovery-249');inner=Path('/mnt/settings-tree-check-249')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=300)
def run(args,name):
 proc=subprocess.run(args,capture_output=True,text=True,timeout=300)
 with (work/(name+'.json')).open('x') as stream:
  json.dump(dict(exit_status=proc.returncode,stdout=proc.stdout,stderr=proc.stderr),stream,indent=2)
 return proc.returncode
def tree(image):
 assert not inner.exists();inner.mkdir(mode=0o700);mounted=False
 try:
  subprocess.run(['mount','-t','ext4','-o','loop,ro,noload,nodev,nosuid,noexec',str(image),str(inner)],check=True);mounted=True
  for row in directories:
   path=inner/row['path'];info=path.stat()
   assert path.is_dir() and not path.is_symlink()
   assert (info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode))==(row['uid'],row['gid'],row['mode'])
   assert os.getxattr(path,'security.selinux').decode().rstrip('\x00')==row['selinux']
  return fingerprint(inner,set())
 finally:
  if mounted:subprocess.run(['umount',str(inner)],check=True,timeout=60)
  inner.rmdir()
assert os.geteuid()==0 and not work.exists() and not outer.exists()
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
trial=json.loads((parent/'settings-journal-trial-248/result.json').read_text())
assert trial==expected_trial and trial['trial_clean_and_provider_preserved']
backup=Path(trial['metadata_backup_path'])
assert backup.parent==parent/'settings-journal-trial-248' and not backup.is_symlink()
assert sha(backup)==trial['metadata_backup_sha256']
firmware=command(['efibootmgr','-v'])
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
work.mkdir(mode=0o700)
assert run(['e2fsck','-f','-n',device],'outer-precheck')==0
outer.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','nodev,nosuid,noexec',device,str(outer)],check=True);mounted=True
 assert outer.stat().st_dev==os.stat(device).st_rdev
 image=outer/'harmony-settings-data-197/data.ext4';active=outer/'harmony-persistent-data-165/data.ext4'
 for path in [image,active]:
  assert path.is_file() and not path.is_symlink() and not path.parent.is_symlink()
  assert path.stat().st_size==8589934592 and stat.S_IMODE(path.stat().st_mode)==0o600
  assert path.stat().st_uid==path.stat().st_gid==0
  assert not command(['losetup','-j',str(path)]).strip()
 assert sha(active)==expected_active
 before_hash=sha(image);assert before_hash==trial['candidate_sha256_before']
 before=tree(image);assert before==trial['existing_tree_before']
 assert sha(image)==before_hash
 undo=work/'candidate-journal.e2undo'
 recovery=run(['e2fsck','-p','-E','journal_only','-z',str(undo),str(image)],'inner-journal')
 assert recovery in [0,1]
 check=run(['e2fsck','-f','-n',str(image)],'inner-readonly-check');assert check==0
 after=tree(image);assert before==after,'visible bytes, types, permissions, owners, xattrs and symlinks must remain unchanged'
 assert sha(active)==expected_active
 after_hash=sha(image)
 with image.open('rb') as stream:os.fsync(stream.fileno())
 subprocess.run(['sync','-f',str(outer)],check=True,timeout=60)
 assert image.stat().st_blocks*512>=8589934592
 assert sha(backup)==trial['metadata_backup_sha256']
 undo.chmod(0o600)
 with undo.open('rb') as stream:os.fsync(stream.fileno())
 result=dict(candidate_before_sha256=before_hash,candidate_after_sha256=after_hash,
  journal_only_exit=recovery,inner_readonly_fsck_exit=check,existing_tree_before=before,
  existing_tree_after=after,full_visible_tree_unchanged=True,tree_excludes_timestamps=True,
  provider_directories_match_original_source_metadata=True,active165_unchanged=True,
  active165_sha256=expected_active,verified_metadata_backup_retained=True,
  undo_path=str(undo),undo_bytes=undo.stat().st_size,undo_sha256=sha(undo),
  manual_fsck_repair_requested=False,boot_requested=False,settings_ui_verified=False)
finally:
 if mounted:subprocess.run(['umount',str(outer)],check=True,timeout=60)
 outer.rmdir()
outer_check=run(['e2fsck','-f','-n',device],'outer-postcheck');assert outer_check==0
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
assert command(['efibootmgr','-v'])==firmware
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
result.update(outer_readonly_fsck_exit=outer_check,lab_partition_unmounted=True,
 ubuntu_default_preserved=True,firmware_unchanged=True,screenoff_timer_enabled_active=True,
 original_images_modified=False,original_services_graceful_shutdown_verified=False)
with (work/'result.json').open('x') as stream:json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    trial = json.loads((ROOT / 'reports/settings-journal-trial-248/result.json').read_text())
    assert trial['trial_clean_and_provider_preserved']
    plan = json.loads((ROOT / 'reports/settingsdata-scaffolding-216/plan.json').read_text())
    directories = [row for row in plan['directories'] if row['path'].startswith('app/el1/0/base/com.ohos.settingsdata')]
    assert len(directories) == 6
    helper = runpy.run_path(str(ROOT / 'next-experiment/prepare-settingsdata-scaffolding-215.py'))
    active = json.loads((ROOT / 'reports/lab-journal-recovery-246/result.json').read_text())['protected_content_hashes_after']['active165']
    code = ('from pathlib import Path\nimport hashlib,json,os,stat,subprocess\n' +
            inspect.getsource(helper['sha']) + '\n' + inspect.getsource(helper['fingerprint']) + '\n' +
            'expected_trial=' + repr(trial) + '\nexpected_active=' + repr(active) +
            '\ndirectories=' + repr(directories) + '\n' + REMOTE)
    compile(code, 'settings-journal-recovery-249.remote', 'exec')
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
