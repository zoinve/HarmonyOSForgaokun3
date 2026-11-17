"""Verify recovered native normal-close markers without inferring a desktop."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import tarfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-095'
    out = folder/'normal-close-runtime-analysis.json'
    assert not out.exists()
    evidence = folder/'runtime-evidence'
    manifest = json.loads((evidence/'retrieval-manifest.json').read_text())
    assert manifest['physical_serial_guard_passed'] and manifest['original_udid_guard_passed']
    hashes = {}
    with tarfile.open(evidence/'original.tar') as tar:
        def load(name):
            with tar.extractfile('./'+name) as stream:
                body = stream.read()
            digest = hashlib.sha256(body).hexdigest()
            row = manifest['files'][name]
            assert len(body) == row['bytes'] and digest == row['sha256'], name
            hashes[name] = digest
            return body
        diagnostic = load('snapshot075-commercial-desktop086.log')
        phase_name = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)),
                         key=lambda n: int(n.split('-')[1].split('.')[0]))
        phase = load(phase_name)
        hilog = load('interactive-hilog030.log')
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    markers = [sanitize(line) for line in diagnostic.splitlines() if line.startswith(b'NORMAL_CLOSE095_')]
    related = []
    for line in hilog.splitlines():
        if len(line) > 16384:
            continue
        if (b'BaseOobeManager' in line or b'sessionExceptionCallback' in line or
            re.search(rb'(?i)(?:Alt.?F4|closeWindow|close.*(?:guide|oobe)|(?:guide|oobe).*close)', line)):
            related.append(sanitize(line))
    text = diagnostic.decode(errors='replace').replace('\x00', '\n')
    observations = []
    for match in re.finditer(r'NORMAL_CLOSE095_OBSERVE target=(130|140)\n(.*?)(?=NORMAL_CLOSE095_OBSERVE|NORMAL_CLOSE095_END|\Z)', text, re.S):
        target, body = match.groups()
        observations.append(dict(target=int(target), focus_windows=re.findall(r'^Focus window: (\d+)$', body, re.M),
            guide_window_rows=[line for line in body.splitlines() if re.match(r'^hwstartupguide\d+\s', line)]))
    result = dict(run=manifest['run'], verified_input_sha256=hashes, diagnostic_markers=markers,
        key_write_success_observed=bool(re.search(rb'^NORMAL_CLOSE095_SENT [^\n]*write_success=1 ', diagnostic, re.M)),
        worker_end_observed=b'NORMAL_CLOSE095_END desktop_not_inferred=1' in diagnostic,
        close_refused_observed=b'NORMAL_CLOSE095_REFUSED' in diagnostic,
        observations=observations, native_lifecycle_lines=related[:200], native_lifecycle_line_count=len(related),
        bounded_target_exit_records=[sanitize(line) for line in phase.splitlines() if re.search(rb'COMMERCIAL087(?:_TARGET_EXIT| target_timeout)', line)],
        normal_close_lifecycle_success_proven=False, desktop_verified=False, interaction_verified=False,
        activation_verified=False, successful_key_write_is_not_window_dismissal=True)
    out.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
