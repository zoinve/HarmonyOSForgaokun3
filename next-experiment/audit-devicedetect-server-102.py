"""Compare two original queries offline without changing target or prior evidence."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(rb'^11-15 (\d\d):(\d\d):(\d\d)\.(\d{3})\s+(\d+)\s+(\d+)\s+(.*)$')


def parse(line):
    match = ROW.match(line)
    if not match:
        return None
    h, m, s, ms, pid, tid = map(int, match.groups()[:6])
    return dict(ms=((h*60+m)*60+s)*1000+ms, pid=pid, tid=tid,
                body=match[7])


def analyze(rows, start, end):
    selected = [r for r in rows if start <= r['ms'] <= end
                and r['pid'] == 930 and r['tid'] == 1455]
    def one(marker):
        found = [r for r in selected if marker in r['body']]
        assert len(found) == 1, (marker, len(found))
        return found[0]
    read = one(b'ReadAbilityFilterList# abilityFilterList length:3')
    stage = one(b'stage = 1; res = 1; err = 0')
    reply = one(b'CheckDeviceAndReplySync# CheckDeviceAndReplySync deviceNum:0')
    return dict(server_pid=930, server_tid=1455,
                request_line=read['line'], stage1_line=stage['line'],
                reply_line=reply['line'],
                request_to_stage1_ms=stage['ms']-read['ms'],
                stage1_to_reply_ms=reply['ms']-stage['ms'],
                request_to_reply_ms=reply['ms']-read['ms'],
                local_info_null_lines=[r['line'] for r in selected
                    if b'GetLocalDeviceNetworkId# localDeviceInfo is nullptr 0' in r['body']],
                evidence=selected)


if __name__ == '__main__':
    source = ROOT/'reports/commercial61-native-101/runtime-evidence'
    output = ROOT/'reports/devicedetect-server-audit-102.json'
    assert not output.exists()
    manifest = json.loads((source/'retrieval-manifest.json').read_text())
    name = 'interactive-hilog030.log'
    body = (source/'raw'/name).read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    assert digest == manifest['files'][name]['sha256']
    assert len(body) == manifest['files'][name]['bytes']
    rows = []
    for number, line in enumerate(body.splitlines(), 1):
        row = parse(line)
        if row:
            row['line'] = number
            rows.append(row)
    base = ((18*60+51)*60)*1000
    first = analyze(rows, base+19000, base+33000)
    replacement = analyze(rows, base+36000, base+37000)
    sanitize = runpy.run_path(str(ROOT/'next-experiment/analyze-original-devicedetect-095.py'))['sanitize']
    for query in (first, replacement):
        for row in query['evidence']:
            row['body'] = sanitize(row['body'])
    result = dict(source_run=manifest['run'], source_sha256=digest,
                  first_query=first, replacement_query=replacement,
                  same_server_thread=True,
                  local_info_null_in_both=bool(first['local_info_null_lines'] and replacement['local_info_null_lines']),
                  causal_claims=dict(remote_service_not_absent=True,
                      missing_local_info_alone_explains_delay=False,
                      exact_wait_or_remote_dependency_identified=False,
                      startup_initialization_overlap_is_only_a_lead=True),
                  original_evidence_modified=False, target_booted=False,
                  desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ('first_query', 'replacement_query')}, indent=2))
    for label, query in [('first', first), ('replacement', replacement)]:
        print(label, json.dumps({k: v for k, v in query.items() if k != 'evidence'}))
