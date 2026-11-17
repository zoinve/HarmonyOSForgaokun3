'''Correlate candidate native markers and offline fsck while preserving active165.'''
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-197-r1'

PAYLOAD=r'''
from pathlib import Path
import hashlib,json,os,re,subprocess
device='/dev/nvme0n1p4';mount=Path('/mnt/settings199-offline')
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not mount.exists()
assert command(['blkid','-p','-o','value','-s','UUID',device]).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
mount.mkdir(mode=0o700);mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True);mounted=True
 assert mount.stat().st_dev==os.stat(device).st_rdev
 active=mount/'harmony-persistent-data-165/data.ext4'
 data=mount/'harmony-settings-data-197/data.ext4'
 assert not active.is_symlink() and not data.is_symlink() and active.stat().st_size==data.stat().st_size==8589934592
 assert not command(['losetup','-j',str(data)]).strip()
 active_hash=sha(active);assert active_hash==expected_active
 assert command(['blkid','-p','-o','value','-s','UUID',str(data)]).strip()=='b8383c4f-844b-46cc-9d67-34a3745b3f1f'
 before=sha(data)
 check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,text=True,timeout=180)
 fields=dict(line.split(':',1) for line in command(['dumpe2fs','-h',str(data)]).splitlines() if ':' in line)
 marker=subprocess.run(['debugfs','-R','cat /.harmony-persistent166/last-boot',str(data)],capture_output=True,text=True,timeout=30)
 marker_value=marker.stdout.strip()
 valid_marker=bool(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',marker_value))
 after=sha(data);assert before==after
 result=dict(filesystem_uuid='b8383c4f-844b-46cc-9d67-34a3745b3f1f',
  candidate_sha256_after_boot=after,offline_fsck_exit=check.returncode,
  filesystem_state=fields.get('Filesystem state','').strip(),
  filesystem_clean=check.returncode==0 and fields.get('Filesystem state','').strip()=='clean',
  native_boot_id=marker_value if valid_marker else None,
  disk_marker_matches_native_runtime=valid_marker and marker_value==expected_boot,
  active165_sha256=active_hash,active165_unchanged_from_predeployment=True,
  candidate_unchanged_by_offline_inspection=True,data_image_mounted=False,
  lab_mounted_readonly_noload=True,repair_requested=False,original_images_modified=False)
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True,timeout=60)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


def main():
    output=REPORT/'settings-data-offline-199.json'
    assert not output.exists()
    assert json.loads((REPORT/'boot-observation.json').read_text())['returned']
    manifest=json.loads((REPORT/'runtime-evidence/retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data=(REPORT/'runtime-evidence/raw'/name).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    phase=max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log',n)),key=lambda n:int(n[6:-4]))
    text=(REPORT/'runtime-evidence/raw'/phase).read_text(errors='replace')
    analysis=runpy.run_path(str(BASE/'analyze-persistent-data-166.py'))['summarize'](
        text,'b8383c4f-844b-46cc-9d67-34a3745b3f1f',None,0)
    pins=re.findall(r'^PERSISTENT172_PIN target=(\d+) data_identity_verified=1$',text,re.M)
    starts=re.findall(r'^NATIVE_ORIGINAL_START real_pid=(\d+) original_pid_in_namespace=1 credentials_unmodified=1$',text,re.M)
    exits=re.findall(r'^COMMERCIAL087_TARGET_EXIT pid=(\d+) status=\d+$',text,re.M)
    target=len(pins)==len(starts)==len(exits)==1 and pins==starts==exits
    flushes=re.findall(r'^PERSISTENT172_FLUSHED target_reaped=1 data_mounts_removed=(\d+) remaining_data_mounts=0 inner_syncfs=1 backing_fsync=1 outer_syncfs=1$',text,re.M)
    flush=len(flushes)==1 and int(flushes[0])>=1 and text.count(
        'PERSISTENT172_FINISH status=0 target_reaped=1 original_services_graceful_shutdown=0\n')==1
    memory=text.count('PERSISTENT168_MEMORY_ARCHIVE previous_log_present=0 preserved=1\n')==1
    extra=re.findall(r'^PERSISTENT173_DIAGNOSTICS_ARCHIVED files=(\d+) fifos=(\d+) app_data_reset=0 original_launch_logic_unchanged=1$',text,re.M)
    fresh_diagnostics=len(extra)==1 and extra[0]==('0','0')
    refused=analysis['storage_refusal_observed'] or bool(re.search(r'^PERSISTENT172_\w*REFUSED',text,re.M))
    analysis.update(inner_and_outer_flush_verified=flush,actual_target_namespace_cleanup_verified=target and flush,
        data_mounts_removed=int(flushes[0]) if len(flushes)==1 else None,
        fresh_candidate_memory_history_verified=memory,fresh_candidate_diagnostics_verified=fresh_diagnostics,
        storage_refusal_observed=refused,offline_consistency_not_inferred=True,
        original_services_graceful_shutdown_verified=False)
    analysis['native_disk_mount_and_flush_verified']=all(analysis[key] for key in [
        'backing_file_identity_and_lock_verified','loop_is_writable_nvme_data',
        'original_runtime_data_mount_observed','original_init_handoff_observed','marker_chain_matches',
        'actual_target_namespace_cleanup_verified','fresh_candidate_memory_history_verified',
        'fresh_candidate_diagnostics_verified']) and not refused and not analysis['seed_reset_observed']
    analysis.update(run=manifest['run'],phase_file=phase,all_retrieved_hashes_verified=True)
    (REPORT/'settings-persistent-analysis-199.json').open('x').write(json.dumps(analysis,indent=2))
    provision=json.loads((ROOT/'reports/settings-data-deploy-198-r3/provision.json').read_text())
    code='expected_active='+repr(provision['active165_before_sha256'])+'\nexpected_boot='+repr(analysis['native_boot_id'])+'\n'+PAYLOAD
    compile(code,'settings-data199-remote','exec')
    ssh=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))['SSH']
    proc=subprocess.run(ssh+['sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=300)
    for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
        (REPORT/('settings-data-offline-199.'+suffix)).open('x').write(data)
    assert proc.returncode==0,proc.stderr
    result=json.loads(proc.stdout)
    result['native_teardown_verified']=analysis['native_disk_mount_and_flush_verified']
    result['full_native_storage_acceptance']=analysis['native_disk_mount_and_flush_verified'] and result['filesystem_clean'] and result['disk_marker_matches_native_runtime']
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
