"""Audit authentic perf samples and errors without turning absence into a claim."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-050'


def fields(text):
    return dict(re.findall(r'(\w+)=([^\s]+)', text))


def samples(text):
    result = []
    for line in text.splitlines():
        if not line.startswith('COMMERCIAL050_HW_SAMPLE '):
            continue
        row = fields(line)
        for name in ['global_pid', 'global_tid', 'ns', 'ip_matches']:
            row[name] = int(row[name])
        for name in ['ip'] + ['x' + str(i) for i in range(7)]:
            row[name] = int(row[name], 16)
        result.append(row)
    return result


def main():
    recovered = (ROOT / 'recovered-evidence/recovery-manifest.json').exists()
    evidence = ROOT / ('recovered-evidence' if recovered else 'runtime-evidence')
    manifest = json.loads((evidence / ('recovery-manifest.json' if recovered else 'retrieval-manifest.json')).read_text())
    for name, item in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    phases = sorted(name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name))
    assert phases
    text = (evidence / 'raw' / phases[-1]).read_text(errors='replace')
    records = samples(text)
    attachments = [fields(line) for line in text.splitlines() if line.startswith('COMMERCIAL050_HW_ATTACHED ')]
    failures = [line for line in text.splitlines() if re.match(r'COMMERCIAL050_HW_(ATTACH_FAILED|MMAP_FAILED|ENABLE_FAILED|MAPPING_WAIT|BAD_SAMPLE|BAD_RING|SLOT_LIMIT)', line)]
    counts = {}
    suppressed = 0
    for line in text.splitlines():
        if not line.startswith('COMMERCIAL050_HW_COUNTS '):
            continue
        row = fields(line)
        counts[(row['tid'], row['event'])] = row
        suppressed += int(row['suppressed_this_drain'])
    names = sorted({row['event'] for row in records})
    summary = {name: dict(samples=sum(row['event'] == name for row in records),
                           first_seconds=min(row['ns'] for row in records if row['event'] == name) / 1e9,
                           last_seconds=max(row['ns'] for row in records if row['event'] == name) / 1e9)
               for name in names}
    result = dict(run=manifest['run'], recovered_evidence=recovered, verified_files=len(manifest['files']),
                  source_phase=phases[-1], attachments=attachments, failures=failures,
                  event_summary=summary, records=records, final_counts=list(counts.values()),
                  lost_samples=sum(int(row['lost']) for row in counts.values()),
                  malformed_records=sum(int(row['malformed']) for row in counts.values()),
                  suppressed_sample_log_lines=suppressed,
                  instruction_pointer_mismatches=sum(not row['ip_matches'] for row in records),
                  request_codes=dict(Counter(str(row['x1'] & 0xffffffff) for row in records if row['event'] == 'request')),
                  registered_callers=dict(Counter(str(row['x1'] & 0xffffffff) for row in records if row['event'] == 'register_agent')),
                  received_callers=dict(Counter(str(row['x3'] & 0xffffffff) for row in records if row['event'] == 'recv_parcel')),
                  normal_target_timeout='COMMERCIAL050 target_timeout=1' in text,
                  target_exit=re.findall(r'COMMERCIAL050_TARGET_EXIT[^\n]+', text),
                  observer_stopped='COMMERCIAL050_HW_STOPPED' in text,
                  absence_is_not_nonexecution_proof=True, actual_desktop_verified=False)
    (ROOT / 'hwbreak-analysis.json').open('x').write(json.dumps(result, indent=2))
    omit = ['records', 'attachments', 'final_counts', 'failures']
    print(json.dumps({**{k: v for k, v in result.items() if k not in omit},
                      'attachment_count': len(attachments), 'failure_count': len(failures),
                      'failure_examples': failures[:8]}, indent=2))


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        rows = samples('COMMERCIAL050_HW_SAMPLE event=request global_pid=42 global_tid=43 ns=123 ip=0x1000 ip_matches=1 x0=0x0 x1=0x11 x2=0x2 x3=0x3 x4=0x4 x5=0x5 x6=0x6')
        assert len(rows) == 1 and rows[0]['x1'] == 17 and rows[0]['global_tid'] == 43
        assert samples('COMMERCIAL050_HW_ATTACH_FAILED tid=43 event=request errno=22') == []
        print('PASS: authentic sample fields, hexadecimal arguments; failed attachment is not a sample')
    else:
        main()
