"""Decode only complete original SceneBoard fault snapshots, exporting stack lines."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'next-experiment'


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-101'
    output = folder/'freeze-stack-analysis.json'
    assert not output.exists()
    source = folder/'runtime-evidence'
    manifest = json.loads((source/'retrieval-manifest.json').read_text())
    name = 'interactive-faults030.log'
    body = (source/'raw'/name).read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    assert digest == manifest['files'][name]['sha256'] and len(body) == manifest['files'][name]['bytes']
    parser = BASE/'native-fault-snapshots-078.py'
    extract = runpy.run_path(str(parser))['extract']
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    accepted, rejected = extract(body)
    seen, records = set(), []
    for row in accepted:
        if 'appfreeze-com.ohos.sceneboard-' not in row['path']:
            continue
        value = hashlib.sha256(row['data']).hexdigest()
        if (row['path'], value) in seen:
            continue
        seen.add((row['path'], value))
        lines = row['data'].splitlines()
        main_blocks = []
        for index, line in enumerate(lines):
            if not re.match(rb'^Tid:\s*4575\b', line):
                continue
            block = []
            for at in range(index, min(index+120, len(lines))):
                candidate = lines[at]
                if at > index and candidate.startswith(b'Tid:'):
                    break
                if re.match(rb'^(?:Tid:|#\d+\s)', candidate):
                    block.append(dict(line=at+1, text=sanitize(candidate)))
            main_blocks.append(block)
        matching = [dict(line=i+1, text=sanitize(line)) for i, line in enumerate(lines)
                    if re.match(rb'^(?:Tid:|#\d+\s)', line) and re.search(
                        rb'GetTrustedDevice|DeviceDetect|device_detect|libcfwk|collaboration|future|pthread_join', line, re.I)]
        records.append(dict(path=row['path'], sample=row['sample'], bytes=len(row['data']),
            sha256=value, main_thread_blocks=main_blocks, matching_stack_frames=matching,
            reason_lines=[sanitize(line) for line in lines if line.startswith((b'Reason:', b'Pid:'))]))
    result = dict(run=manifest['run'], verified_input_sha256=digest,
        snapshot_parser_sha256=hashlib.sha256(parser.read_bytes()).hexdigest(),
        complete_snapshots=len(accepted), rejected_snapshots=rejected,
        original_sceneboard_faults=records, raw_decoded_faults_not_exported=True,
        original_evidence_modified=False, target_booted=False, desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'rejected_snapshots'}, indent=2))
