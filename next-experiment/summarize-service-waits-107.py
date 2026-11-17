"""Preserve a compact, hash-verified account of the actual query wait path."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-107'
    output = folder / 'service-wait-summary.json'
    assert not output.exists()
    analysis_bytes = (folder / 'server-event-analysis.json').read_bytes()
    analysis = json.loads(analysis_bytes)
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    def read(name):
        data = (folder / 'runtime-evidence/raw' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest['files'][name]['sha256']
        return data
    hilog = read('interactive-hilog030.log')
    phase = read('phase-120.log')
    dm, collaboration = analysis['captures']
    assert dm['role'] == 'device_manager' and collaboration['role'] == 'CollaborationFwk'
    assert dm['inside_client_query'] and collaboration['inside_client_query']
    request_tid = analysis['events']['server_read_request']['tid']
    request = [thread for thread in collaboration['all_thread_blocks'] if re.match(r'Tid:\s*' + str(request_tid) + r',', thread['header'])]
    assert len(request) == 1
    def contains(thread, *tokens):
        text = '\n'.join(frame['module_and_symbol'] for frame in thread['frames'])
        return all(token in text for token in tokens)
    assert contains(request[0], 'mutex::lock', 'GetLocalDeviceInfo', 'GetTrustedWithAbilityFilterListInner')
    init = [thread for thread in collaboration['all_thread_blocks'] if contains(thread, 'InitPackageName', 'BinderInvoker::WaitForCompletion')]
    memory_mutex = [thread for thread in dm['all_thread_blocks'] if contains(thread, 'libmemmgrclient', 'SetCritical', 'mutex::lock')]
    memory_lookup = [thread for thread in dm['all_thread_blocks'] if contains(thread, 'libmemmgrclient', 'GetSystemAbilityWrapper', 'usleep')]
    zombie = []
    lines = phase.splitlines()
    for index, line in enumerate(lines):
        if line == b'Name:\tl410_memmgr_noh' and index + 1 < len(lines):
            zombie.append(dict(line=index + 1, preceding_header=sanitize(lines[index - 1]),
                               name=sanitize(line), state=sanitize(lines[index + 1])))
    selected = []
    scene = analysis['events']['client_start']['pid']
    for index, line in enumerate(hilog.splitlines(), 1):
        if len(line) > 1200:
            continue
        if (b'/device_manager/MM:' in line and b'MemMgrService is null' in line) or (
                ('kill pid ' + str(scene) + ',').encode() in line and b'Kill Reason:THREAD_BLOCK_6S' in line):
            selected.append(dict(line=index, text=sanitize(line)))
    events = analysis['events']
    result = dict(run=analysis['run'], analysis_sha256=hashlib.sha256(analysis_bytes).hexdigest(),
        raw_inputs_verified=True, actual_request_thread=request[0],
        collaboration_initialization_wait_threads=init,
        memory_client_mutex_waiter_headers=[thread['header'] for thread in memory_mutex],
        memory_client_system_ability_lookup_threads=memory_lookup,
        memory_wrapper_zombie_observations=zombie, original_memory_null_and_watchdog_logs=selected,
        client_query_ms=events['client_end']['milliseconds'] - events['client_start']['milliseconds'],
        request_to_stage1_ms=events['server_stage1']['milliseconds'] - events['server_read_request']['milliseconds'],
        stage1_to_reply_ms=events['server_reply']['milliseconds'] - events['server_stage1']['milliseconds'],
        actual_request_sdk_mutex_wait_proven=True,
        missing_memory_service_dependency_observed=True,
        exact_cross_process_binder_transaction_link_not_captured=True,
        mutex_owner_addresses_not_captured=True,
        original_memory_wrapper_failure_errno_not_captured=True,
        oobe_bypass_not_proven=True, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(run=result['run'], client_query_ms=result['client_query_ms'],
        actual_request_tid=request_tid, memory_mutex_waiters=len(memory_mutex),
        memory_lookup_threads=len(memory_lookup), memory_wrapper_zombies=len(zombie),
        desktop_verified=False), indent=2))
