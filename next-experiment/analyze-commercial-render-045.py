"""Correlate immutable native scene, presentation and passive task evidence."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-045'


def fields(text):
    return dict(re.findall(r'(\w+)=([^\s]+)', text))


def main():
    raw = ROOT / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (raw / name).read_bytes()
        assert len(data) == item['bytes']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
    hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace')
    faults = (raw / 'interactive-faults030.log').read_text(errors='replace')
    lines = hilog.splitlines()
    frames = [fields(line) for line in dict.fromkeys(faults.splitlines())
              if line.startswith('COMMERCIAL030_FRAME ')]
    flush = [dict(line=n, text=line) for n, line in enumerate(lines, 1)
             if 'com.ohos.sceneboard/Ace' in line and 'ArkUi flush first frame messages.' in line]
    times = []
    for item in flush:
        match = re.search(r'01-01 (\d+):(\d+):(\d+\.\d+)', item['text'])
        if match:
            times.append((int(match[1]) - 8) * 3600 + int(match[2]) * 60 + float(match[3]))
    tasks = {}
    pattern = re.compile(r'^COMMERCIAL039_TASK ([^\n]+)\n(.*?)(?=^COMMERCIAL|\Z)',
                         re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(faults):
        row = fields(match[1])
        key = tuple(row[k] for k in ['sample', 'pid', 'tid'])
        task = tasks.setdefault(key, dict(sample=int(key[0]), pid=int(key[1]), tid=int(key[2])))
        task[row['file']] = dict(bytes=int(row['bytes']), errno=int(row['errno']),
                                 text=match[2].strip())
    scene = [dict(line=n, text=line) for n, line in enumerate(lines, 1)
             if '/render_service/' in line and 'SetIsOnTheTree' in line]
    warnings = [dict(line=n, text=line) for n, line in enumerate(lines, 1)
                if '/render_service/' in line and 'no application agent registered' in line]
    rs_pid = next(t['pid'] for t in tasks.values()
                  if t.get('comm', {}).get('text') == 'render_service')
    rs_tasks = [t for t in tasks.values() if t['pid'] == rs_pid]
    post = [r for r in frames if times and int(r['mono_us']) / 1e6 >= min(times)]
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
                  missing_application_agent_warnings=warnings, scene_transitions=scene,
                  first_flush=flush, first_flush_guest_seconds=times, frames=frames,
                  last_frame_seconds=max((int(r['mono_us']) / 1e6 for r in frames), default=None),
                  postflush_frames=len(post),
                  postflush_sampled_nonblack_frames=sum(int(r['output_nonblack']) > 0 for r in post),
                  render_service_tasks=rs_tasks,
                  render_service_waits=dict(Counter(t.get('wchan', {}).get('text', 'missing') for t in rs_tasks)),
                  actual_desktop_verified=False,
                  absence_of_warning_is_not_direct_registration_pid_observation=True,
                  sparse_pixel_samples_are_not_full_frame_proof=True)
    with (ROOT / 'render-analysis.json').open('x') as out:
        json.dump(result, out, indent=2)
    print(json.dumps({k: result[k] for k in ['verified_files', 'missing_application_agent_warnings',
          'first_flush_guest_seconds', 'last_frame_seconds', 'postflush_frames',
          'postflush_sampled_nonblack_frames', 'render_service_waits', 'actual_desktop_verified']}, indent=2))


if __name__ == '__main__':
    main()
