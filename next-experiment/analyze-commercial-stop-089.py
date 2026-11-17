"""Keep stop request, native response, and subsequent process evidence separate."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent


def analyze(body):
    text = body.decode('utf-8', errors='replace').replace('\x00', '\n')
    ready = re.findall(r'DESKTOP089_DOCK_READY scene_pid=(\d+) stable_interval=10', text)
    requests = re.findall(r'DESKTOP089_STOP_BEGIN guide_pids=([^\n]+)', text)
    results = [int(n) for n in re.findall(r'DESKTOP089_STOP_RESULT exit_status=(\d+)', text)]
    samples = []
    for target, pid, block in re.findall(r'DESKTOP089_SAMPLE target=(\d+) ready_pid=(\d*)\n(.*?)(?=DESKTOP089_SAMPLE|DESKTOP089_END|\Z)', text, re.S):
        scene = re.search(r'DESKTOP089_SCENE_PIDS([^\n]*)', block)
        guide = re.search(r'DESKTOP089_GUIDE_PIDS([^\n]*)', block)
        samples.append(dict(target=int(target), ready_pid=int(pid) if pid else None,
            scene_pids=[int(n) for n in scene.group(1).split()] if scene else None,
            guide_pids=[int(n) for n in guide.group(1).split()] if guide else None))
    return dict(source_sha256=hashlib.sha256(body).hexdigest(), begin_observed='DESKTOP089_BEGIN' in text,
        end_observed='DESKTOP089_END' in text, ready_pids=[int(n) for n in ready],
        stop_request_count=len(requests), stop_exit_statuses=results,
        original_aa_zero_status=results == [0], samples=samples,
        guide_absent_at_all_samples=bool(samples) and all(s['guide_pids'] == [] for s in samples),
        same_ready_scene_at_all_samples=bool(samples) and all(s['scene_pids'] == [s['ready_pid']] for s in samples),
        original_aa_output=text.split('DESKTOP089_STOP_BEGIN', 1)[1].split('DESKTOP089_STOP_RESULT', 1)[0] if requests else None,
        oobe_completed_proven=False, desktop_verified=False, interaction_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-089'
    path = report / 'runtime-evidence/raw/snapshot075-commercial-desktop086.log'
    result = analyze(path.read_bytes())
    (report / 'single-stop-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
