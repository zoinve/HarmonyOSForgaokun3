"""Analyze real original-method probe records without claiming missing calls."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-046'


def fields(text):
    return dict(re.findall(r'(\w+)=([^\s]+)', text))


def parse_trace(text):
    records = []
    seen = set()
    pattern = re.compile(r'^\s*(.+)-(\d+)\s+\[(\d+)\].*?\s(\d+\.\d+):\s+(\w+):\s+(.*)$')
    for line in text.splitlines():
        match = pattern.match(line)
        if not match or line in seen:
            continue
        seen.add(line)
        records.append(dict(comm=match[1].strip(), global_tid=int(match[2]),
                            cpu=int(match[3]), seconds=float(match[4]),
                            event=match[5], arguments=fields(match[6]), raw=line))
    return records


def main():
    raw = ROOT / 'runtime-evidence/raw'
    manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (raw / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    phases = sorted(name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name))
    name = phases[-1]
    text = (raw / name).read_text(errors='replace')
    pattern = re.compile(r'^COMMERCIAL046_OUTER_STREAM_BEGIN ([^\n]+)\n(.*?)'
                         r'^COMMERCIAL046_OUTER_STREAM_END ([^\n]+)$', re.MULTILINE | re.DOTALL)
    streams = []
    all_records = []
    profiles = []
    for match in pattern.finditer(text):
        begin, end = fields(match[1]), fields(match[3])
        assert begin['path'] == end['path']
        if begin['path'] not in ['/sys/kernel/tracing/trace', '/sys/kernel/tracing/uprobe_profile']:
            continue
        row = dict(path=begin['path'], limit=int(begin['limit']),
                   bytes=int(end['bytes']), eof=int(end['eof']), errno=int(end['errno']))
        streams.append(row)
        if begin['path'].endswith('/trace'):
            all_records.extend(parse_trace(match[2]))
        else:
            profiles.append(match[2])
    unique = {row['raw']: row for row in all_records}
    records = sorted(unique.values(), key=lambda row: (row['seconds'], row['global_tid']))
    events = sorted({row['event'] for row in records})
    summary = {event: dict(count=sum(row['event'] == event for row in records),
                           first=min(row['seconds'] for row in records if row['event'] == event),
                           last=max(row['seconds'] for row in records if row['event'] == event))
               for event in events}
    ready = [line for line in text.splitlines() if line.startswith('COMMERCIAL046_TRACE_READY ')]
    failures = [line for line in text.splitlines() if line.startswith('COMMERCIAL046_TRACE_SETUP_FAILED ')]
    result = dict(run=manifest['run'], verified_files=len(manifest['files']), source_phase=name,
                  setup_ready=ready, setup_failures=failures, streams=streams,
                  possibly_truncated_streams=sum(not row['eof'] for row in streams),
                  event_summary=summary, records=records, profiles=profiles,
                  registered_callers=dict(Counter(row['arguments'].get('caller', 'missing')
                      for row in records if row['event'] == 'register_agent')),
                  received_callers=dict(Counter(row['arguments'].get('caller', 'missing')
                      for row in records if row['event'] == 'recv_parcel')),
                  absence_is_not_nonexecution_proof=True, actual_desktop_verified=False)
    with (ROOT / 'trace-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({key: result[key] for key in ['verified_files', 'setup_ready', 'setup_failures',
          'possibly_truncated_streams', 'event_summary', 'registered_callers', 'received_callers',
          'actual_desktop_verified']}, indent=2))


if __name__ == '__main__':
    main()
