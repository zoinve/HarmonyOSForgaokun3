"""Authenticate retrieved files and extract only public service/request evidence."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-073'
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
body = (raw / 'interactive-faults030.log').read_bytes()
pattern = (rb'COMMERCIAL043_STREAM_BEGIN sample=(\d+) pid=(\d+) path=([^\n]+) limit=(\d+)\n'
           rb'(.*?)\nCOMMERCIAL043_STREAM_END sample=\1 pid=\2 path=\3 bytes=(\d+) eof=(\d+) errno=(\d+)')
streams = []
for match in re.finditer(pattern, body, re.S):
    path = match[3].decode()
    if not (path == '/data/native-allocator-073.trace' or
            'l410-kylin-' in path or re.fullmatch(r'/proc/\d+/(maps|status)', path)):
        continue
    assert len(match[5]) == int(match[6]) <= int(match[4])
    streams.append(dict(sample=int(match[1]), pid=int(match[2]), path=path,
                        bytes=int(match[6]), eof=int(match[7]), errno=int(match[8]),
                        body=match[5].decode(errors='replace')))
complete = [s for s in streams if s['eof'] == 1 and s['errno'] == 0]
traces = [s for s in complete if s['path'] == '/data/native-allocator-073.trace']
requests = []
if traces:
    selected = max(traces, key=lambda s: (s['bytes'], s['sample']))
    for line in selected['body'].splitlines():
        match = re.fullmatch(r'COMMERCIAL073_ALLOC_REQUEST sequence=(\d+) pid=(\d+) uid=(\d+) width=(\d+) height=(\d+) format=(-?\d+) usage=(0x[0-9a-f]+) expected=(\d+) public_interface=1', line)
        assert match, line
        values = match.groups()
        row = dict(zip(['sequence', 'pid', 'uid', 'width', 'height', 'format', 'usage', 'expected'],
                       [int(v, 16) if i == 6 else int(v) for i, v in enumerate(values)]))
        assert row['uid'] == 3041
        row['usage_hex'] = hex(row['usage'])
        requests.append(row)
    assert len(requests) <= 128
    assert len({r['sequence'] for r in requests}) == len(requests)
services = [line.decode(errors='replace') for line in body.splitlines()
            if line.startswith(b'COMMERCIAL073_PUBLIC_SERVICE ')]
hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace').splitlines()
failures = [line for line in hilog if any(token in line for token in
    ['Start codec failed: cannot allocate buffers', 'AllocMem: AllocMem failed, ec = -2',
     'Alloc surface buffer failed'])]
result = dict(run=manifest['run'], verified_files=len(manifest['files']),
              public_requests=requests, public_services=services, streams=streams,
              allocation_failure_messages=failures, allocator_request_trace_complete=bool(traces),
              request_log_limit=128, request_log_saturated=len(requests) == 128,
              public_requests_are_bounded_samples_not_all_allocations=True,
              request_log_does_not_record_return_values=True,
              private_memory_read=False, desktop_verified=False, interaction_verified=False)
with (root / 'allocator-analysis.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps(dict(requests=len(requests), services=len(services), streams=len(streams),
                     formats=sorted({r['format'] for r in requests}),
                     allocation_failure_lines=len(failures), desktop_verified=False), indent=2))
