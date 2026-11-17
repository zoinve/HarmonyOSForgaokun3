"""Analyze immutable original evidence; consumption is not execution or pixels."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-043'


def fields(text):
    return dict(re.findall(r'(\w+)=([^\s]+)', text))


def main():
    evidence = ROOT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == item['bytes']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
    hilog = (evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')
    faults = (evidence / 'raw/interactive-faults030.log').read_text(errors='replace')
    records = []
    for number, line in enumerate(hilog.splitlines(), 1):
        if 'IPC043 phase=' not in line:
            continue
        row = fields(line.split('IPC043 ', 1)[1])
        for key in list(row):
            if key not in ['phase', 'device']:
                row[key] = int(row[key])
        row['source_line'] = number
        records.append(row)
    keys = ['pid', 'serial', 'interface', 'handle', 'code', 'end']
    entered = {tuple(row[k] for k in keys): row for row in records if row['phase'] == 'enter'}
    pairs = []
    for row in records:
        if row['phase'] != 'return':
            continue
        before = entered.get(tuple(row[k] for k in keys))
        pairs.append(dict(return_record=row, enter_record=before,
                          ioctl_success=row['result'] == 0,
                          kernel_consumed_through_command=row['consumed'] >= row['end']))
    streams = []
    pattern = re.compile(r'^COMMERCIAL043_STREAM_BEGIN ([^\n]+)\n(.*?)'
                         r'^COMMERCIAL043_STREAM_END ([^\n]+)$', re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(faults):
        begin, end = fields(match[1]), fields(match[3])
        assert all(begin[k] == end[k] for k in ['sample', 'pid', 'path'])
        row = {k: int(v) if k != 'path' else v for k, v in end.items()}
        body = match[2]
        if row['path'].endswith('/maps'):
            row['mapped_paths'] = sorted({line.split(maxsplit=5)[5] for line in body.splitlines()
                                          if len(line.split(maxsplit=5)) == 6})
        else:
            row['body'] = body
        streams.append(row)
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
                  observed_records=len(records), records=records, paired_returns=pairs,
                  processes={str(pid): dict(
                      codes=dict(Counter(f"{r['interface']}:{r['code']}:{r['phase']}"
                                         for r in records if r['pid'] == pid)),
                      devices=sorted({r['device'] for r in records if r['pid'] == pid}))
                      for pid in sorted({r['pid'] for r in records})},
                  streams=streams, kernel_consumption_is_not_service_execution=True,
                  missing_logs_are_not_proof_of_absence=True, actual_desktop_verified=False)
    with (ROOT / 'binder-analysis.json').open('x') as out:
        json.dump(result, out, indent=2)
    print(json.dumps(dict(verified_files=result['verified_files'], records=len(records),
                          processes=result['processes'],
                          consumed_successful_returns=sum(p['ioctl_success'] and p['kernel_consumed_through_command'] for p in pairs),
                          streams=len(streams), stream_errors=dict(Counter(str(s['errno']) for s in streams)),
                          complete_maps=[dict(pid=s['pid'], bytes=s['bytes'], eof=s['eof'], errno=s['errno'])
                                         for s in streams if s['path'].endswith('/maps')],
                          actual_desktop_verified=False), indent=2))


if __name__ == '__main__':
    main()
