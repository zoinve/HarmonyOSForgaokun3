"""Correlate observed aa argument records and original OOBE recovery."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def aa_commands(text):
    commands, current = [], {}
    pattern = re.compile(r'^\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}\s+(\d+)\s+\d+\s+I C01303/aa/AATool: .*argv_\[(\d+)\]: (.*)$')
    for number, line in enumerate(text.splitlines(), 1):
        match = pattern.match(line)
        if not match:
            continue
        pid, index, value = match.groups()
        index = int(index)
        if index == 0:
            row = dict(pid=int(pid), first_line=number, argv={})
            commands.append(row)
            current[pid] = row
        if pid in current:
            current[pid]['argv'][index] = value
    for row in commands:
        row['argv_records_contiguous'] = sorted(row['argv']) == list(range(max(row['argv']) + 1))
        row['argv'] = [value for _, value in sorted(row['argv'].items())]
    return commands


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-114'
    output = folder / 'oobe-single-launch-analysis.json'
    assert not output.exists()
    reference = json.loads((folder / 'reference-runtime-analysis.json').read_text())
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    raw = folder / 'runtime-evidence/raw'
    def load(name):
        data = (raw / name).read_bytes()
        assert sha(data) == manifest['files'][name]['sha256']
        assert len(data) == manifest['files'][name]['bytes']
        return data.decode(errors='replace')
    def sha(data):
        return hashlib.sha256(data).hexdigest()
    log = load('interactive-hilog030.log')
    script_log = load('snapshot075-commercial-direct-desktop075.log')
    commands = aa_commands(log)
    scene_starts = [row for row in commands if 'start' in row['argv'] and 'com.ohos.sceneboard' in row['argv']]
    guide_stops = [row for row in commands if 'force-stop' in row['argv'] and 'com.huawei.hmos.hwstartupguide' in row['argv']]
    scenes = {int(pid) for row in reference['samples'] for pid in row['scene_pids'] or []}
    events = runpy.run_path(str(Path(__file__).with_name('audit-oobe-recovery-106.py')))['events']
    timeline = {str(pid): events(log, pid) for pid in sorted(scenes)}
    marker = 'OOBE114_EXISTING_SCENEBOARD_NO_SECOND_START' in script_log
    relaunched = reference['original_relaunch_observed']
    result = dict(run=manifest['run'],
        hilog_sha256=manifest['files']['interactive-hilog030.log']['sha256'],
        second_start_removed_guard_marker_observed=marker,
        existing_scene_missing_guard_observed='OOBE114_MISSING_EXISTING_SCENEBOARD' in script_log,
        observed_scene_start_commands=scene_starts, observed_guide_stop_commands=guide_stops,
        captured_argv_not_proof_of_log_completeness=True,
        original_recovery_timeline=timeline, original_guide_relaunch_observed=relaunched,
        focus_samples=reference['samples'],
        conclusion=('Removing second startup owner was not sufficient to prevent original guide recovery'
                    if marker and relaunched else 'Interpret original lifecycle and pixels; no desktop claim'),
        desktop_verified=False, interaction_verified=False, activation_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'original_recovery_timeline'}, indent=2))
