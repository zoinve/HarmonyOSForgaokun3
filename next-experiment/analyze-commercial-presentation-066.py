"""Require complete bounded trace streams and complete frame records."""
from pathlib import Path
import hashlib
import json
import re

R = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-066'
FIELDS = set('sequence mono_us fb ppm_good source_status source_nonblack source_samples source_hash output_valid output_nonblack output_samples output_hash client_w client_h client_stride client_format gpu_owned'.split())


def streams(raw):
    pattern = (rb'COMMERCIAL043_STREAM_BEGIN sample=(\d+) pid=0 path=/data/native-perf-023.trace limit=(\d+)\n'
               rb'(.*?)\nCOMMERCIAL043_STREAM_END sample=\1 pid=0 path=/data/native-perf-023.trace bytes=(\d+) eof=(\d+) errno=(\d+)')
    result = []
    for match in re.finditer(pattern, raw, re.S):
        body = match[3]
        count, limit = int(match[4]), int(match[2])
        assert len(body) == count and count <= limit, 'Trace stream byte-count mismatch'
        result.append(dict(sample=int(match[1]), limit=limit, bytes=count,
                           eof=int(match[5]), errno=int(match[6]), body=body))
    return result


def frames(raw):
    result = []
    for line in raw.splitlines():
        if not line.startswith(b'COMMERCIAL030_FRAME '):
            continue
        pairs = re.findall(rb'(\w+)=(-?\d+)', line)
        row = {key.decode(): int(value) for key, value in pairs}
        if set(row) == FIELDS and len(pairs) == len(FIELDS):
            result.append(row)
    return result


if __name__ == '__main__':
    raw = R / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (raw / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    snapshots = streams((raw / 'interactive-faults030.log').read_bytes())
    complete = [s for s in snapshots if s['eof'] == 1 and s['errno'] == 0]
    assert complete, 'No complete presentation trace was recovered'
    selected = max(complete, key=lambda s: (s['bytes'], s['sample']))
    recovered = frames(selected['body'])
    assert recovered and len({r['sequence'] for r in recovered}) == len(recovered)
    assert [r['mono_us'] for r in recovered] == sorted(r['mono_us'] for r in recovered)
    render = json.loads((R / 'render-analysis.json').read_text())
    first = min(render['first_flush_guest_seconds'], default=None)
    post = [r for r in recovered if first is not None and r['mono_us'] >= first * 1000000]
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
                  streams=[{k: v for k, v in s.items() if k != 'body'} for s in snapshots],
                  selected_sample=selected['sample'], selected_bytes=selected['bytes'],
                  selected_sha256=hashlib.sha256(selected['body']).hexdigest(),
                  full_trace_eof_verified=True, first_flush_seconds=first,
                  frames=recovered, last_frame_seconds=recovered[-1]['mono_us'] / 1000000,
                  postflush_frames=len(post),
                  postflush_source_nonblack_frames=sum(r['source_nonblack'] > 0 for r in post),
                  postflush_output_nonblack_frames=sum(r['output_nonblack'] > 0 for r in post),
                  sparse_samples_not_full_desktop_verification=True, desktop_verified=False)
    (R / 'complete-presentation.trace').open('xb').write(selected['body'])
    (R / 'presentation-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ('frames', 'streams')}, indent=2))
