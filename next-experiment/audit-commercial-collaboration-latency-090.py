"""Read-only service-side timing audit; do not bypass authentication failures."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent
LINE = re.compile(r'^(\d\d-\d\d)\s+(\d\d:\d\d:\d\d\.\d+)\s+(\d+)\s+(\d+)\s+([A-Z])\s+(.+)$')


def audit(body):
    rows = []
    for number, line in enumerate(body.decode('utf-8', errors='replace').splitlines(), 1):
        match = LINE.match(line)
        if match:
            date, clock, pid, tid, level, message = match.groups()
            rows.append(dict(line=number, date=date, clock=clock, pid=int(pid), tid=int(tid), level=level, message=message))
    service = {r['pid'] for r in rows if '/CollaborationFwk/DeviceDetect:' in r['message'] and 'DeviceDetectService constructor' in r['message']}
    assert len(service) == 1, service
    pid = service.pop()
    auth = [r for r in rows if r['pid'] == pid and 'CheckAuthentication Failed' in r['message']]
    pending, calls = {}, []
    for row in rows:
        if row['pid'] != pid:
            continue
        tid = row['tid']
        if 'ReadAbilityFilterList# abilityFilterList length:' in row['message']:
            pending[tid] = dict(begin=row, stages=[])
        elif tid in pending:
            if 'GetTrustedDeviceListWithAbilityFilter# event =' in row['message']:
                pending[tid]['stages'].append(row)
            elif 'CheckDeviceAndReplySync# CheckDeviceAndReplySync deviceNum:' in row['message']:
                call = pending.pop(tid)
                begin = call['begin']
                start = datetime.strptime('2026-' + begin['date'] + ' ' + begin['clock'], '%Y-%m-%d %H:%M:%S.%f')
                end = datetime.strptime('2026-' + row['date'] + ' ' + row['clock'], '%Y-%m-%d %H:%M:%S.%f')
                call['end'] = row
                call['elapsed_ms'] = round((end-start).total_seconds()*1000, 3)
                calls.append(call)
    return dict(source_sha256=hashlib.sha256(body).hexdigest(), original_collaboration_pid=pid,
        authentication_failure_count=len(auth), authentication_failure_threads=len({r['tid'] for r in auth}),
        authentication_failure_counts_per_second=dict(Counter(r['date']+' '+r['clock'].split('.')[0] for r in auth)),
        service_filter_to_reply_calls=calls, incomplete_requests=list(pending.values()),
        sample_authentication_failures=auth[:2]+auth[-2:],
        authentication_failure_cause_not_proven=True, no_security_check_changes=True,
        service_latency_does_not_alone_identify_lock_owner=True)


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial-collaboration-latency-audit-090'
    assert not folder.exists()
    results = {}
    for number in ('088', '089'):
        path = ROOT / f'reports/commercial61-native-{number}/runtime-evidence/raw/interactive-hilog030.log'
        results[number] = audit(path.read_bytes())
    folder.mkdir()
    (folder/'result.json').open('x').write(json.dumps(results, indent=2))
    for number, result in results.items():
        print(json.dumps(dict(experiment=number, pid=result['original_collaboration_pid'],
            authentication_failure_count=result['authentication_failure_count'],
            authentication_failure_threads=result['authentication_failure_threads'],
            request_elapsed_ms=[c['elapsed_ms'] for c in result['service_filter_to_reply_calls']]), indent=2))
