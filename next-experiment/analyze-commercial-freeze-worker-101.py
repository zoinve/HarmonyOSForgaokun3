"""Preserve complete thread stacks containing the original DeviceDetect wait."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'next-experiment'


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-101'
    output = folder/'freeze-worker-analysis.json'
    assert not output.exists()
    manifest = json.loads((folder/'runtime-evidence/retrieval-manifest.json').read_text())
    body = (folder/'runtime-evidence/raw/interactive-faults030.log').read_bytes()
    assert hashlib.sha256(body).hexdigest() == manifest['files']['interactive-faults030.log']['sha256']
    accepted, _ = runpy.run_path(str(BASE/'native-fault-snapshots-078.py'))['extract'](body)
    selected = next(row for row in accepted if 'appfreeze-com.ohos.sceneboard-' in row['path'])
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    lines = selected['data'].splitlines()
    blocks, current = [], []
    for number, line in enumerate(lines, 1):
        if line.startswith(b'Tid:'):
            if current:
                blocks.append(current)
            current = [(number, line)]
        elif current and re.match(rb'^#\d+\s+pc\s+[0-9a-fA-F]+\s+', line):
            current.append((number, line))
    if current:
        blocks.append(current)
    chosen = []
    for block in blocks:
        if not any(b'libcollabfwk_devicedetect_client.z.so' in line for _, line in block):
            continue
        frames = []
        for number, line in block:
            frame = re.match(rb'^#(\d+)\s+pc\s+([0-9a-fA-F]+)\s+(.*)', line)
            if frame:
                frames.append(dict(line=number, index=int(frame[1]), code_offset=int(frame[2], 16), module_and_symbol=sanitize(frame[3])))
        chosen.append(dict(thread=sanitize(block[0][1]), frames=frames))
    result = dict(run=manifest['run'], original_path=selected['path'],
        complete_fault_sha256=hashlib.sha256(selected['data']).hexdigest(),
        threads=chosen, offsets_are_code_locations_not_identity=True,
        original_evidence_modified=False, raw_decoded_fault_not_exported=True)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
