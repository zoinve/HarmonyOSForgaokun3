"""Analyze the dedicated original DFX capture without altering raw evidence."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'next-experiment'
FRAME = re.compile(rb'^#(\d+)\s+pc\s+([0-9a-fA-F]+)\s+(.*)')


def stack_blocks(body, sanitize):
    blocks = []
    current = None
    for number, line in enumerate(body.splitlines(), 1):
        if line.startswith(b'Tid:'):
            current = dict(header=sanitize(line), line=number, frames=[])
            blocks.append(current)
        elif current is not None and (match := FRAME.match(line)):
            current['frames'].append(dict(line=number, index=int(match[1]),
                code_offset=int(match[2], 16), module_and_symbol=sanitize(match[3])))
    return blocks


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-104'
    output = folder/'server-stack-analysis.json'
    assert not output.exists()
    source = folder/'runtime-evidence'
    manifest = json.loads((source/'retrieval-manifest.json').read_text())
    hashes = {}
    def read(name):
        body = (source/'raw'/name).read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        assert digest == manifest['files'][name]['sha256']
        assert len(body) == manifest['files'][name]['bytes']
        hashes[name] = digest
        return body
    name = 'snapshot075-commercial-server-stack104.log'
    assert name in manifest['files'], 'Dedicated observer log not exported; do not infer capture'
    body = read(name)
    hilog = read('interactive-hilog030.log')
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    begin = re.findall(rb'SERVER104_CAPTURE_BEGIN server_pid=(\d+) scene_pids=([^\n]*)', body)
    native = re.findall(rb'APP_STACK_RESULT pid=(\d+) result=(-?\d+) reason=([^\n]*)', body)
    ends = re.findall(rb'SERVER104_CAPTURE_END status=(\d+) success_not_inferred=1', body)
    blocks = stack_blocks(body, sanitize)
    focus = [block for block in blocks if any(
        any(token in frame['module_and_symbol'] for token in (
            'CollaborationFwkServiceUtils', 'DeviceDetect', 'DeviceManager',
            'libcollaborationfwk_service_base', 'libcollabfwk_devicedetect',
            '__shared_mutex_base', 'BinderInvoker::WaitForCompletion')) for frame in block['frames'])]
    server_pid = int(begin[0][0]) if len(begin) == 1 else None
    lines = []
    for number, line in enumerate(hilog.splitlines(), 1):
        if len(line) > 16384:
            continue
        if ((b'/CollaborationFwk/' in line and any(token in line for token in (
            b'ReadAbilityFilterList#', b'GetTrustedDeviceListWithAbilityFilter#',
            b'GetLocalDeviceNetworkId#', b'UpdateLocalDeviceInfoInLock',
            b'CheckDeviceAndReplySync#')))
            or (b'/com.ohos.sceneboard/' in line and any(token in line for token in (
                b'device_picker_client.cpp:388]', b'device_picker_client.cpp:396]')))
            or (any(token in line for token in (b'DumpCatchWithTimeout', b'Processdump SigVal',
                b'DumpCatchRemote', b'APP_STACK_RESULT')))):
            lines.append(dict(line=number, text=sanitize(line)))
    result = dict(run=manifest['run'], verified_input_sha256=hashes,
        dedicated_log_complete_marker=b'SERVER104_END desktop_not_inferred=1' in body,
        unique_capture_begin=len(begin) == 1, server_pid=server_pid,
        capture_exit_statuses=[int(value) for value in ends],
        native_api_results=[dict(pid=int(pid), result=int(code), reason=sanitize(reason)) for pid, code, reason in native],
        native_user_stack_reported=(len(native) == 1 and int(native[0][1]) == 0 and bool(blocks)),
        stack_thread_count=len(blocks), frame_count=sum(len(block['frames']) for block in blocks),
        relevant_thread_blocks=focus,
        marker_and_time_lines=[dict(line=i+1, text=sanitize(line)) for i, line in enumerate(body.splitlines())
            if line.startswith((b'SERVER104_', b'APP_STACK_RESULT', b'Timestamp:', b'Pid:', b'Process name:'))
            or re.fullmatch(rb'\d+\.\d+ \d+\.\d+', line)],
        correlated_original_logs=lines, observation_can_perturb_timing=True,
        query_overlap_not_assumed=True, original_evidence_modified=False,
        desktop_verified=False, interaction_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in (
        'relevant_thread_blocks', 'correlated_original_logs', 'marker_and_time_lines')}, indent=2))
