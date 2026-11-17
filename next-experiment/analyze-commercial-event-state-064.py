"""Analyze original public CLI output, with no inference from missing snapshots."""
from pathlib import Path
import hashlib
import json
import re
import runpy

B = Path(__file__).resolve().parent
R = B.parent / 'reports/commercial61-native-064'


def parse_streams(native):
    pattern = (r'COMMERCIAL064_OUTER_STREAM_BEGIN path=(\S*/commercial-event-state064\.log) limit=(\d+)\n'
               r'(.*?)\nCOMMERCIAL064_OUTER_STREAM_END path=\1 bytes=(\d+) eof=(\d+) errno=(\d+)')
    return [dict(path=m[1], limit=int(m[2]), text=m[3], bytes=int(m[4]),
                 eof=int(m[5]), errno=int(m[6]), byte_count_matches=len(m[3].encode()) == int(m[4]))
            for m in re.finditer(pattern, native, re.S)]


def main():
    assert not (R / 'event-analysis.json').exists(), 'Preserve numbered evidence'
    evidence = R / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        blob = (evidence / 'raw' / name).read_bytes()
        assert len(blob) == item['bytes']
        assert hashlib.sha256(blob).hexdigest() == item['sha256']
    native = sorted((evidence / 'raw').glob('phase-*.log'))[-1].read_bytes().decode(errors='replace')
    snapshots = parse_streams(native)
    valid = [s for s in snapshots if s['eof'] == 1 and s['errno'] == 0 and s['byte_count_matches']]
    selected = max(valid, key=lambda s: s['bytes']) if valid else None
    text = selected['text'] if selected else ''
    if selected:
        (R / 'event-state064.log').open('x').write(text)
    acl = [dict(key=m[1], output=m[2], result=int(m[3])) for m in re.finditer(
        r'COMMERCIAL064_ACL_BEGIN key=(\S+)\n(.*?)COMMERCIAL064_ACL_END result=(\d+)\n', text, re.S)]
    rounds = []
    for m in re.finditer(r'COMMERCIAL064_SNAPSHOT_BEGIN round=(\d+)\n(.*?)COMMERCIAL064_SNAPSHOT_END round=\1\n', text, re.S):
        values = [dict(key=v[1], output=v[2], result=int(v[3])) for v in re.finditer(
            r'COMMERCIAL064_VALUE_BEGIN key=(\S+)\n(.*?)COMMERCIAL064_VALUE_END result=(\d+)\n', m[2], re.S)]
        rounds.append(dict(round=int(m[1]), values=values))
    expected = runpy.run_path(str(B / 'commercial-event-state-064.py'))['KEYS']
    complete = (len(rounds) == 5 and [r['round'] for r in rounds] == list(range(5))
                and all([v['key'] for v in r['values']] == expected for r in rounds))
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
                  snapshots=[{k: v for k, v in s.items() if k != 'text'} for s in snapshots],
                  selected_bytes=selected['bytes'] if selected else None, effective_acl_output=acl,
                  rounds=rounds, complete_expected_rounds=complete,
                  script_end_observed='COMMERCIAL064_EVENT_DIAGNOSTICS_END' in text,
                  command_success_not_parameter_true_proof=True,
                  missing_output_not_event_absence_proof=True, desktop_verified=False)
    (R / 'event-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
