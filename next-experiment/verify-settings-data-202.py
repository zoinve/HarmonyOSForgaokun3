'''Inspect201 storage and archive evidence without assuming native teardown succeeded.'''
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-201'
PREVIOUS='76d33584-471a-4e78-bab5-e417a6d5c30b'


def main():
    output=REPORT/'settings-data-offline-202.json'
    assert not output.exists()
    assert json.loads((REPORT/'boot-observation.json').read_text())['returned']
    manifest=json.loads((REPORT/'runtime-evidence/retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data=(REPORT/'runtime-evidence/raw'/name).read_bytes()
        assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
    phase=max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)),key=lambda name:int(name[6:-4]))
    text=(REPORT/'runtime-evidence/raw'/phase).read_text(errors='replace')
    counts=re.findall(r'^PERSISTENT166_RUNTIME .* archived=(\d+)$',text,re.M)
    assert len(counts)==1
    archived=int(counts[0]);assert 0<=archived<=5
    analysis=runpy.run_path(str(BASE/'analyze-persistent-data-166.py'))['summarize'](
        text,'b8383c4f-844b-46cc-9d67-34a3745b3f1f',PREVIOUS,archived)
    pins=re.findall(r'^PERSISTENT172_PIN target=(\d+) data_identity_verified=1$',text,re.M)
    starts=re.findall(r'^NATIVE_ORIGINAL_START real_pid=(\d+) original_pid_in_namespace=1 credentials_unmodified=1$',text,re.M)
    exits=re.findall(r'^COMMERCIAL087_TARGET_EXIT pid=(\d+) status=\d+$',text,re.M)
    target=len(pins)==len(starts)==len(exits)==1 and pins==starts==exits
    flushes=re.findall(r'^PERSISTENT172_FLUSHED target_reaped=1 data_mounts_removed=(\d+) remaining_data_mounts=0 inner_syncfs=1 backing_fsync=1 outer_syncfs=1$',text,re.M)
    flush=len(flushes)==1 and int(flushes[0])>=1 and text.count(
        'PERSISTENT172_FINISH status=0 target_reaped=1 original_services_graceful_shutdown=0\n')==1
    memory=text.count('PERSISTENT168_MEMORY_ARCHIVE previous_log_present=1 preserved=1\n')==1
    extra=re.findall(r'^PERSISTENT173_DIAGNOSTICS_ARCHIVED files=(\d+) fifos=(\d+) app_data_reset=0 original_launch_logic_unchanged=1$',text,re.M)
    diagnostic_archive=len(extra)==1 and int(extra[0][0])>=1
    refused=analysis['storage_refusal_observed'] or bool(re.search(r'^PERSISTENT(?:172|201)_\w*(?:REFUSED|FAILED)',text,re.M))
    reasons={1:'truncated_line',2:'row_limit',3:'field_parse',4:'invalid_mount_id',5:'separator_missing',
             6:'path_decode',7:'duplicate_mount_id',8:'stream_error',9:'empty_mount_table',
             10:'selected_root',11:'duplicate_selected_path'}
    plan_rejections=[dict(reason=int(reason),classification=reasons.get(int(reason),'unknown'),parsed_rows=int(rows))
        for reason,rows in re.findall(r'^PERSISTENT201_PLAN_REFUSED reason=(\d+) parsed_rows=(\d+) raw_paths_exported=0$',text,re.M)]
    analysis.update(run=manifest['run'],phase_file=phase,all_retrieved_hashes_verified=True,
        inner_and_outer_flush_verified=flush,actual_target_namespace_cleanup_verified=target and flush,
        data_mounts_removed=int(flushes[0]) if len(flushes)==1 else None,
        previous_memory_log_archive_observed=memory,additional_diagnostic_archive_observed=diagnostic_archive,
        storage_refusal_observed=refused,planner_rejections=plan_rejections,
        marker_reported_archived_objects=archived,archive_count_requires_offline_correlation=True,
        settings_window_verified=False,original_services_graceful_shutdown_verified=False)
    analysis['native_disk_mount_and_flush_verified']=all(analysis[key] for key in [
        'backing_file_identity_and_lock_verified','loop_is_writable_nvme_data','original_runtime_data_mount_observed',
        'original_init_handoff_observed','marker_chain_matches','actual_target_namespace_cleanup_verified',
        'previous_memory_log_archive_observed','additional_diagnostic_archive_observed']) and not refused and not analysis['seed_reset_observed']
    (REPORT/'settings-persistent-analysis-202.json').open('x').write(json.dumps(analysis,indent=2))
    payload=runpy.run_path(str(BASE/'verify-settings-data-199.py'))['PAYLOAD']
    payload=payload.replace('/mnt/settings199-offline','/mnt/settings202-offline')
    anchor='finally:\n if mounted:'
    assert payload.count(anchor)==1
    additional=''' names=['native-perf-023.trace','native-scanout-013.ppm','native-allocator-073.trace','native-full-068','native-full-075']
 history='/.harmony-persistent166/'+expected_boot+'/'
 objects={}
 for name in names:
  info=subprocess.run(['debugfs','-R','stat '+history+name,str(data)],capture_output=True,text=True,timeout=30)
  objects[name]='Inode:' in info.stdout
 memory=subprocess.run(['debugfs','-R','stat '+history+'commercial-memmgr108.log',str(data)],capture_output=True,text=True,timeout=30)
 result.update(previous_diagnostic_objects_archived=objects,
  archived_count_matches_runtime=sum(objects.values())==expected_archived,
  previous_memory_log_archived='Inode:' in memory.stdout and 'Type: regular' in memory.stdout)
'''
    payload=payload.replace(anchor,additional+anchor,1)
    active=json.loads((ROOT/'reports/settings-data-deploy-198-r3/provision.json').read_text())['active165_before_sha256']
    code='expected_active='+repr(active)+'\nexpected_boot='+repr(analysis['native_boot_id'])+'\nexpected_archived='+repr(archived)+'\n'+payload
    compile(code,'settings202-offline-remote','exec')
    ssh=runpy.run_path(str(BASE/'deploy-settings-data-198.py'))['SSH']
    proc=subprocess.run(ssh+['sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=300)
    for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
        (REPORT/('settings-data-offline-202.'+suffix)).open('x').write(data)
    assert proc.returncode==0,proc.stderr
    result=json.loads(proc.stdout)
    result['native_teardown_verified']=analysis['native_disk_mount_and_flush_verified']
    result['full_native_storage_acceptance']=all([analysis['native_disk_mount_and_flush_verified'],
        result['filesystem_clean'],result['disk_marker_matches_native_runtime'],
        result['archived_count_matches_runtime'],result['previous_memory_log_archived']])
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
