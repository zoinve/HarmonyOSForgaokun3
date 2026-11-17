"""Trial candidate journal recovery on metadata and fingerprint live file bytes."""
from pathlib import Path
import inspect
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settings-journal-trial-248'
REMOTE = r'''
os.environ['LC_ALL']='C';os.umask(0o077)
device='/dev/nvme0n1p4'
parent=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')
work=parent/'settings-journal-trial-248'
outer=Path('/mnt/settings-journal-trial-248');inner=Path('/mnt/settings-tree-before-248')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=300)
def metadata(path,filesystem):
 text=command(['debugfs','-R','stat /'+path,str(filesystem)])
 assert 'Inode:' in text and 'Type: directory' in text
 rows=[line for line in text.splitlines() if not re.match(r'\s*(?:[acm]time:|crtime:|Inode checksum:|Generation:)',line)]
 return hashlib.sha256(('\n'.join(rows)+'\n').encode()).hexdigest()
def run(args,name):
 proc=subprocess.run(args,capture_output=True,text=True,timeout=300)
 with (work/(name+'.json')).open('x') as stream:
  json.dump(dict(exit_status=proc.returncode,stdout=proc.stdout,stderr=proc.stderr),stream,indent=2)
 return proc.returncode
assert os.geteuid()==0 and not work.exists() and not outer.exists() and not inner.exists()
assert command(['blkid','-p','-s','UUID','-o','value',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
work.mkdir(mode=0o700);outer.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(outer)],check=True);mounted=True
 assert outer.stat().st_dev==os.stat(device).st_rdev
 image=outer/'harmony-settings-data-197/data.ext4';active=outer/'harmony-persistent-data-165/data.ext4'
 assert not image.is_symlink() and image.stat().st_size==8589934592
 assert not command(['losetup','-j',str(image)]).strip()
 assert sha(active)==expected_active
 before_hash=sha(image);assert before_hash==expected_candidate
 inner.mkdir(mode=0o700);inner_mounted=False
 try:
  subprocess.run(['mount','-t','ext4','-o','loop,ro,noload,nodev,nosuid,noexec',str(image),str(inner)],check=True);inner_mounted=True
  for row in directories:
   path=inner/row['path'];info=path.stat()
   assert path.is_dir() and not path.is_symlink()
   assert (info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode))==(row['uid'],row['gid'],row['mode'])
   assert os.getxattr(path,'security.selinux').decode().rstrip('\x00')==row['selinux']
  tree=fingerprint(inner,set())
 finally:
  if inner_mounted:subprocess.run(['umount',str(inner)],check=True,timeout=60)
  inner.rmdir()
 before={row['path']:metadata(row['path'],image) for row in directories}
 backup=work/'candidate-before.qcow2';trial=work/'candidate-trial.raw'
 assert run(['e2image','-Q',str(image),str(backup)],'metadata-backup')==0
 assert run(['e2image','-r',str(backup),str(trial)],'trial-conversion')==0
 for path in [backup,trial]:
  path.chmod(0o600)
  with path.open('rb') as stream:os.fsync(stream.fileno())
  assert path.stat().st_blocks*512<1024**3
 assert trial.stat().st_size==image.stat().st_size
 assert {row['path']:metadata(row['path'],trial) for row in directories}==before
 journal=run(['e2fsck','-p','-E','journal_only','-z',str(work/'trial-journal.e2undo'),str(trial)],'trial-journal')
 check=run(['e2fsck','-f','-n',str(trial)],'trial-readonly')
 after={row['path']:metadata(row['path'],trial) for row in directories}
 assert sha(image)==before_hash and sha(active)==expected_active
 result=dict(candidate_sha256_before=before_hash,active165_unchanged=True,
  source_candidate_written=False,existing_tree_before=tree,tree_excludes_timestamps=True,
  original_provider_directory_metadata_verified=True,provider_metadata_before=before,
  provider_metadata_after=after,provider_metadata_unchanged=before==after,
  journal_only_exit=journal,trial_readonly_fsck_exit=check,
  trial_clean_and_provider_preserved=journal in [0,1] and check==0 and before==after,
  metadata_backup_path=str(backup),metadata_backup_sha256=sha(backup),
  metadata_backup_bytes=backup.stat().st_size,trial_allocated_bytes=trial.stat().st_blocks*512,
  metadata_only_trial_does_not_prove_file_contents=True,boot_requested=False)
finally:
 if mounted:subprocess.run(['umount',str(outer)],check=True,timeout=60)
 outer.rmdir()
result['lab_partition_unmounted']=True
with (work/'result.json').open('x') as stream:json.dump(result,stream,indent=2)
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    assert not REPORT.exists()
    recovery = json.loads((ROOT / 'reports/lab-journal-recovery-246/result.json').read_text())
    assert recovery['outer_readonly_fsck_exit'] == 0
    plan = json.loads((ROOT / 'reports/settingsdata-scaffolding-216/plan.json').read_text())
    directories = [row for row in plan['directories'] if row['path'].startswith('app/el1/0/base/com.ohos.settingsdata')]
    assert len(directories) == 6
    helper = runpy.run_path(str(ROOT / 'next-experiment/prepare-settingsdata-scaffolding-215.py'))
    hashes = recovery['protected_content_hashes_after']
    code = ('from pathlib import Path\nimport hashlib,json,os,re,stat,subprocess\n' +
            inspect.getsource(helper['sha']) + '\n' + inspect.getsource(helper['fingerprint']) + '\n' +
            'expected_active=' + repr(hashes['active165']) + '\nexpected_candidate=' + repr(hashes['candidate197']) +
            '\ndirectories=' + repr(directories) + '\n' + REMOTE)
    compile(code, 'settings-journal-trial-248.remote', 'exec')
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
