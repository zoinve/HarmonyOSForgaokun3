"""Verify final capture and namespace-exit records against retrieved hashes."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-121'
    output = folder / 'data-snapshot-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    phases = sorted((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)),
                    key=lambda n: int(n.split('-')[1].split('.')[0]))
    assert phases
    name = phases[-1]
    raw = (folder / 'runtime-evidence/raw' / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == manifest['files'][name]['sha256']
    assert len(raw) == manifest['files'][name]['bytes']
    records = [line.decode('ascii') for line in raw.splitlines() if
               re.search(rb'OOBE121_|COMMERCIAL087_TARGET_EXIT|COMMERCIAL087 target_timeout|NATIVE_ORIGINAL_END|NATIVE_DIAGNOSTIC_END', line)]
    capture = re.findall(rb'OOBE121_CAPTURE_RESULT status=(\d+) thaw=(\d+) private_path=([^\r\n ]+)', raw)
    complete = b'OOBE121_DATA_SNAPSHOT complete=1 bytes=8589934592 target_private_only=1 settings_modified=0' in raw
    result = dict(run=manifest['run'], final_phase=name, final_phase_sha256=hashlib.sha256(raw).hexdigest(),
        records=records, complete_snapshot_marker_observed=complete,
        capture_and_thaw_succeeded=(len(capture) == 1 and capture[0][:2] == (b'0', b'0') and complete),
        private_data_not_in_exported_run=True, settings_modified=False,
        desktop_verified=False, interaction_verified=False)
    assert not any('private-oobe121' in n or n.endswith('.ext4') for n in manifest['files'])
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
