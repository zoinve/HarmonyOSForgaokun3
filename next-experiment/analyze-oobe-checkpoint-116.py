"""Verify observed checkpoint, original process lifecycle and query timing."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'


def query_pairs(lines):
    pattern = re.compile(rb'^(\d\d-\d\d) (\d\d):(\d\d):(\d\d)\.(\d{3})\s+(\d+)\s+(\d+) .*CFWKProxy: .*GetTrustedDeviceListWithAbilityFilter# (start|end)$')
    rows, pending = [], {}
    for number, line in enumerate(lines, 1):
        match = pattern.match(line)
        if not match:
            continue
        day, h, m, s, ms, pid, tid, action = match.groups()
        if pid != tid:
            continue
        stamp = ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)
        key = int(pid)
        if action == b'start':
            row = dict(pid=key, day=day.decode(), start_ms=stamp, start_line=number,
                       end_ms=None, end_line=None, duration_ms=None)
            rows.append(row)
            pending[key] = row
        elif key in pending:
            row = pending.pop(key)
            row['end_ms'], row['end_line'] = stamp, number
            if row['day'] == day.decode() and stamp >= row['start_ms']:
                row['duration_ms'] = stamp - row['start_ms']
    return rows


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-116'
    output = folder / 'oobe-checkpoint-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    verified, missing = {}, []
    def load(name, optional=False):
        if name not in manifest['files']:
            assert optional, name
            missing.append(name)
            return b''
        data = (folder / 'runtime-evidence/raw' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest['files'][name]['sha256']
        assert len(data) == manifest['files'][name]['bytes']
        verified[name] = manifest['files'][name]['sha256']
        return data
    log = load('interactive-hilog030.log')
    gate = load('snapshot075-commercial-collaboration-ready116.log', optional=True)
    reference = load('snapshot075-commercial-direct-desktop075.log', optional=True)
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    lines = log.splitlines()
    launches = []
    for number, line in enumerate(lines, 1):
        match = re.search(rb'Child process com.ohos.sceneboard success pid (\d+)', line)
        if match:
            launches.append(dict(pid=int(match.group(1)), line=number, text=sanitize(line)))
    scene_pids = {row['pid'] for row in launches}
    life = []
    for number, line in enumerate(lines, 1):
        if len(line) >= 4096:
            continue
        relevant = (b'BaseOobeManager:' in line or b'Child process com.huawei.hmos.hwstartupguide success pid ' in line or
                    b'aa/AATool:' in line and (b'argv_[0]:' in line or b'argv_[1]:' in line or b'force stop process successfully' in line) or
                    b'OnAddSystemAbilityEvent# RegisterHichainProofExceptionStatusCallback, ret: 0' in line or
                    any(('kill pid ' + str(pid) + ',').encode() in line and b'Kill Reason:THREAD_BLOCK_6S' in line for pid in scene_pids))
        if relevant:
            life.append(dict(line=number, text=sanitize(line)))
    failures = [line.decode(errors='replace') for line in gate.splitlines() if b'CFWK116_REFUSED' in line]
    gate_event = re.search(rb'^CFWK116_ORIGINAL_EVENT pid=(\d+) text=(.*)$', gate, re.M)
    event_raw_verified = False
    checkpoint_line = None
    if gate_event:
        pid, original_event = gate_event.groups()
        header = re.match(rb'^\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}\s+(\d+)\s+', original_event)
        assert header and header.group(1) == pid
        event_raw_verified = original_event in lines
        if event_raw_verified:
            checkpoint_line = lines.index(original_event) + 1
    queries = query_pairs(lines)
    expected_frames = ('full-ready-068', 'full-ready-075')
    frames = {name: name in manifest['files'] for name in expected_frames}
    final_phase = max((name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)),
                      key=lambda name: int(name.split('-')[1].split('.')[0]))
    phase = load(final_phase)
    result = dict(run=manifest['run'], verified_input_sha256=verified,
        gate_log=sanitize(gate), gate_checkpoint_observed=b'CFWK116_CHECKPOINT_OBSERVED' in gate,
        gate_event_matches_hashed_raw_hilog=event_raw_verified, gate_refusals=failures,
        checkpoint_original_hilog_line=checkpoint_line,
        checkpoint_precedes_first_observed_scene_launch=(checkpoint_line < launches[0]['line']
            if checkpoint_line is not None and launches else None),
        checkpoint_not_proof_of_full_service_readiness=True,
        missing_optional_observation_files=missing, scene_launches=launches, query_pairs=queries,
        original_lifecycle=life, expected_full_frame_exports_present=frames,
        reference_force_stop_success_observed=b'force stop process successfully' in reference,
        final_phase=final_phase, bounded_exit_records=[sanitize(line) for line in phase.splitlines()
            if re.search(rb'COMMERCIAL087(?:_TARGET_EXIT| target_timeout)', line)],
        desktop_verified=False, interaction_verified=False, activation_verified=False,
        log_success_not_desktop_acceptance=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key not in ('original_lifecycle', 'gate_log')}, indent=2))
