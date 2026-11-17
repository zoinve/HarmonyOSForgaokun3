"""Verify immutable runtime inputs and reference-stop/relaunch observations."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import tarfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-099'
    output = folder/'reference-runtime-analysis.json'
    assert not output.exists()
    evidence = folder/'runtime-evidence'
    manifest = json.loads((evidence/'retrieval-manifest.json').read_text())
    assert manifest['physical_serial_guard_passed'] and manifest['original_udid_guard_passed']
    hashes = {}
    with tarfile.open(evidence/'original.tar') as archive:
        def load(name):
            with archive.extractfile('./'+name) as stream:
                body = stream.read()
            row = manifest['files'][name]
            digest = hashlib.sha256(body).hexdigest()
            assert len(body) == row['bytes'] and digest == row['sha256'], name
            hashes[name] = digest
            return body
        reference = load('snapshot075-commercial-direct-desktop075.log')
        diagnostic = load('snapshot075-commercial-desktop086.log')
        hilog = load('interactive-hilog030.log')
        phase_name = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)),
                         key=lambda n: int(n.split('-')[1].split('.')[0]))
        phase = load(phase_name)
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    text = reference.decode(errors='replace').replace('\x00', '\n')
    samples = []
    for match in re.finditer(r'REFERENCE099_SAMPLE target=(\d+)\n(.*?)REFERENCE099_SAMPLE_END target=\1', text, re.S):
        target, body = match.groups()
        guide = re.search(r'^REFERENCE099_GUIDE_PIDS ([^\n]*)', body, re.M)
        scene = re.search(r'^REFERENCE099_SCENE_PIDS ([^\n]*)', body, re.M)
        samples.append(dict(target=int(target),
            guide_pids=guide.group(1).split() if guide else None,
            scene_pids=scene.group(1).split() if scene else None,
            focus_windows=re.findall(r'^Focus window: (\d+)$', body, re.M),
            guide_window_rows=[line for line in body.splitlines() if re.match(r'^hwstartupguide\d+\s', line)]))
    life = []
    for number, line in enumerate(hilog.splitlines(), 1):
        if len(line) > 16384:
            continue
        if b'BaseOobeManager:' in line or b'sessionExceptionCallback' in line:
            life.append(dict(line=number, text=sanitize(line)))
    result = dict(run=manifest['run'], verified_input_sha256=hashes,
        reference_log=sanitize(reference), reference_marker_observed=b'NATIVE_DESKTOP_READY' in reference,
        aa_force_stop_success_message_observed=b'force stop process successfully' in reference,
        samples=samples, original_oobe_lifecycle=life,
        original_relaunch_observed=any(b'BaseOobeManager: start oobe again' in line for line in hilog.splitlines()),
        reference_worker_launch_marker_observed=b'REFERENCE099_BEGIN' in diagnostic,
        old_normal_close_worker_observed=b'NORMAL_CLOSE095_BEGIN' in diagnostic,
        bounded_target_exit_records=[sanitize(line) for line in phase.splitlines()
                                    if re.search(rb'COMMERCIAL087(?:_TARGET_EXIT| target_timeout)', line)],
        final_phase=phase_name, desktop_verified=False, interaction_verified=False,
        activation_verified=False, marker_and_pid_absence_are_not_desktop_proof=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ('reference_log', 'original_oobe_lifecycle')}, indent=2))
