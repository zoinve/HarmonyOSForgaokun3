"""Keep runtime teardown, offline consistency and desktop acceptance distinct."""
from pathlib import Path
import hashlib
import json
import re
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-173'

if __name__ == '__main__':
    evidence = REPORT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    latest = max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)),key=lambda name:int(name[6:-4]))
    text = (evidence / 'raw' / latest).read_text(errors='replace')
    repaired = json.loads((ROOT / 'reports/persistent-source-recovery-171/result.json').read_text())
    previous = json.loads((ROOT / 'reports/commercial61-native-168/persistent-runtime-analysis.json').read_text())['native_boot_id']
    assert repaired['filesystem_clean'] and repaired['native_boot_marker_retained']
    uuid = json.loads((ROOT / 'reports/persistent-data-165/provision.json').read_text())['filesystem_uuid']
    result = runpy.run_path(str(BASE / 'analyze-persistent-data-166.py'))['summarize'](text,uuid,previous,5)
    pins = re.findall(r'^PERSISTENT172_PIN target=(\d+) data_identity_verified=1$',text,re.M)
    starts = re.findall(r'^NATIVE_ORIGINAL_START real_pid=(\d+) original_pid_in_namespace=1 credentials_unmodified=1$',text,re.M)
    exits = re.findall(r'^COMMERCIAL087_TARGET_EXIT pid=(\d+) status=\d+$',text,re.M)
    target = len(pins) == len(starts) == len(exits) == 1 and pins == starts == exits
    flushes = re.findall(r'^PERSISTENT172_FLUSHED target_reaped=1 data_mounts_removed=(\d+) remaining_data_mounts=0 inner_syncfs=1 backing_fsync=1 outer_syncfs=1$',text,re.M)
    flush = len(flushes) == 1 and int(flushes[0]) >= 1 and text.count(
        'PERSISTENT172_FINISH status=0 target_reaped=1 original_services_graceful_shutdown=0\n') == 1
    memory = text.count('PERSISTENT168_MEMORY_ARCHIVE previous_log_present=1 preserved=1\n') == 1
    extra = re.findall(r'^PERSISTENT173_DIAGNOSTICS_ARCHIVED files=(\d+) fifos=(\d+) app_data_reset=0 original_launch_logic_unchanged=1$',text,re.M)
    archived = len(extra) == 1 and int(extra[0][0]) >= 1
    refused = result['storage_refusal_observed'] or bool(re.search(r'^PERSISTENT172_\w*REFUSED',text,re.M))
    result.update(inner_and_outer_flush_verified=flush,actual_target_namespace_cleanup_verified=target and flush,
        data_mounts_removed=int(flushes[0]) if len(flushes)==1 else None,
        memory_prerequisite_log_archived=memory,extra_diagnostic_archive_verified=archived,
        extra_diagnostic_files_archived=int(extra[0][0]) if len(extra)==1 else None,
        extra_diagnostic_fifos_archived=int(extra[0][1]) if len(extra)==1 else None,
        storage_refusal_observed=refused,offline_consistency_not_inferred=True,
        original_services_graceful_shutdown_verified=False,
        run=manifest['run'],phase_file=latest,all_retrieved_hashes_verified=True)
    result['native_disk_mount_and_flush_verified'] = all(result[key] for key in [
        'backing_file_identity_and_lock_verified','loop_is_writable_nvme_data',
        'original_runtime_data_mount_observed','original_init_handoff_observed','marker_chain_matches',
        'actual_target_namespace_cleanup_verified','memory_prerequisite_log_archived','extra_diagnostic_archive_verified'
    ]) and not refused and not result['seed_reset_observed']
    (REPORT / 'persistent-runtime-analysis.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    if not result['native_disk_mount_and_flush_verified']:raise SystemExit('Native persistent storage acceptance incomplete')
