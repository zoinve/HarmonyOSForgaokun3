"""Preserve original SceneBoard freeze/kill/restart evidence from completed 114."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-114'
    output = folder / 'oobe-scene-restart-analysis.json'
    assert not output.exists()
    evidence = folder / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    def load(name):
        data = (evidence / 'raw' / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest['files'][name]['sha256']
        assert len(data) == manifest['files'][name]['bytes']
        return data
    log = load('interactive-hilog030.log')
    faults = load('interactive-faults030.log')
    reference = load('snapshot075-commercial-direct-desktop075.log')
    sanitize = runpy.run_path(str(BASE / 'analyze-original-devicedetect-095.py'))['sanitize']
    short = [(i, line) for i, line in enumerate(log.splitlines(), 1) if len(line) < 16384]
    launches = [(i, line) for i, line in short if b'Child process com.ohos.sceneboard success pid ' in line]
    assert len(launches) == 2
    pids = [int(re.search(rb'success pid (\d+)', line).group(1)) for _, line in launches]
    old, new = pids
    kill = [(i, line) for i, line in short
            if ('kill pid ' + str(old) + ', ret:0, Kill Reason:THREAD_BLOCK_6S').encode() in line]
    assert len(kill) == 1
    died = [(i, line) for i, line in short
            if ('com.ohos.sceneboard with pid ' + str(old) + ' exit with signal:9').encode() in line]
    assert len(died) == 1 and launches[0][0] < kill[0][0] < died[0][0] < launches[1][0]
    patterns = [rb'aa/AATool:.*argv_\[[01]\]:', rb'aa/AATool:.*force stop process successfully',
                rb'BaseOobeManager:.*(?:start oobe|sessionExceptionCallback)',
                rb'OnSessionException: bundleName=com.huawei.hmos.hwstartupguide',
                rb'CFWKProxy:.*GetTrustedDeviceListWithAbilityFilter#',
                rb'AppDfr:.*(?:THREAD_BLOCK|NotifyAppFault)',
                rb'AppMS:.*(?:APP_FREEZE|Kill Reason:THREAD_BLOCK_6S)']
    selected = [(i, line) for i, line in short if any(re.search(pattern, line) for pattern in patterns)]
    selected += launches + died
    parser = runpy.run_path(str(BASE / 'native-fault-snapshots-078.py'))['extract']
    accepted, rejected = parser(faults)
    records, seen = [], set()
    for row in accepted:
        if 'appfreeze-com.ohos.sceneboard-' not in row['path']:
            continue
        data = row['data']
        digest = hashlib.sha256(data).hexdigest()
        if (row['path'], digest) in seen:
            continue
        seen.add((row['path'], digest))
        lines = data.splitlines()
        match = re.search(rb'^Pid:\s*(\d+)', data, re.M)
        assert match
        pid = int(match.group(1))
        blocks = []
        for index, line in enumerate(lines):
            if not re.match(('^Tid:\\s*' + str(pid) + r'\b').encode(), line):
                continue
            block = []
            for at in range(index, min(index + 160, len(lines))):
                candidate = lines[at]
                if at > index and candidate.startswith(b'Tid:'):
                    break
                if re.match(rb'^(Tid:|#\d+\s)', candidate):
                    block.append(dict(line=at + 1, text=sanitize(candidate)))
            blocks.append(block)
        records.append(dict(path=row['path'], pid=pid, sample=row['sample'], sha256=digest,
            bytes=len(data), main_thread_blocks=blocks,
            reason_lines=[sanitize(line) for line in lines if line.startswith((b'Reason:', b'Pid:'))]))
    initial = reference.split(b'REFERENCE099_SAMPLE target=', 1)[0]
    initial_scene_rows = [sanitize(line) for line in initial.splitlines() if line.startswith(b'SCBDesktop')]
    initial_focus = re.findall(rb'^Focus window: (\d+)$', initial, re.M)
    missing = [name for name in ('full-ready-068', 'full-ready-075') if name not in manifest['files']]
    result = dict(run=manifest['run'], verified_input_sha256={name: manifest['files'][name]['sha256']
        for name in ('interactive-hilog030.log', 'interactive-faults030.log', 'snapshot075-commercial-direct-desktop075.log')},
        initial_scene_pid=old, replacement_scene_pid=new, original_appms_freeze_kill_proven=True,
        initial_desktop_rows=initial_scene_rows, initial_focus_windows=[int(value) for value in initial_focus],
        initial_focus_is_window_metadata_not_pixel_proof=True,
        timeline=[dict(line=i, text=sanitize(line)) for i, line in sorted(set(selected))],
        original_scene_freezes=records, rejected_fault_snapshot_count=len(rejected),
        expected_capture_files_missing=missing, capture_analyzers_failed_before_successful_output=True,
        observed_aa_invocations=[dict(line=i, text=sanitize(line)) for i, line in short if b'aa/AATool:' in line and b'argv_[0]:' in line],
        aa_logs_only_first_two_arguments_so_bundle_association_not_proven_by_argv_alone=True,
        guide_absence_not_stable=True, desktop_verified=False, interaction_verified=False,
        kernel_adaptation_performed=False, watchdog_and_original_recovery_unchanged=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key not in ('timeline', 'original_scene_freezes')}, indent=2))
    for record in records:
        print(json.dumps(dict(pid=record['pid'], reason=record['reason_lines'], main_thread_blocks=record['main_thread_blocks']), indent=2))
