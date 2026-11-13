"""Analyze bounded real callback journals; never certify desktop FPS from them."""
from collections import defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics

NUMBERS = ('pid', 'uid', 'id', 'fb', 'submit_us', 'callback_us', 'drm_seq',
           'drm_sec', 'drm_usec', 'timestamp_monotonic', 'matched', 'result', 'error')


def analyze(raw):
    groups = defaultdict(lambda: defaultdict(list))
    rejected_lines = 0
    limited = b'NATIVE_PRESENT043 kind=limit ' in raw
    for line in raw.splitlines():
        if b'NATIVE_PRESENT043 ' not in line:
            continue
        if line.count(b'NATIVE_PRESENT043 ') != 1:
            rejected_lines += 1
            continue
        pairs = re.findall(rb'([a-z_]+)=([^\s]+)', line.split(b'NATIVE_PRESENT043 ', 1)[1])
        if len(dict(pairs)) != len(pairs):
            rejected_lines += 1
            continue
        fields = {k.decode(): v.decode(errors='replace') for k, v in pairs}
        if fields.get('kind') in ('clock', 'limit'):
            continue
        try:
            for key in NUMBERS:
                if not re.fullmatch(r'-?\d+', fields[key]):
                    raise ValueError(key)
                fields[key] = int(fields[key])
            if fields['uid'] != 3036 or fields['pid'] <= 0 or fields['id'] <= 0:
                raise ValueError('not an original-composer journal identity')
        except (KeyError, ValueError):
            rejected_lines += 1
            continue
        group = groups[(fields['pid'], fields['id'])][fields['kind']]
        if fields not in group:  # cumulative snapshots are not new presentations
            group.append(fields)

    accepted, rejected_ids = [], []
    for key, kinds in groups.items():
        submits, completions = kinds.get('submit', []), kinds.get('complete', [])
        if len(submits) != 1 or len(completions) != 1 or kinds.get('submit_failed') or kinds.get('overlap'):
            rejected_ids.append(list(key))
            continue
        sub, event = submits[0], completions[0]
        consistent = all(sub[k] == event[k] for k in ('origin', 'fb', 'submit_us', 'timestamp_monotonic'))
        if not (consistent and event['origin'] in ('client', 'cursor') and event['fb'] > 0
                and event['matched'] == 1 and event['timestamp_monotonic'] == 1
                and event['submit_us'] > 0 and event['callback_us'] >= event['submit_us']
                and 0 <= event['drm_seq'] < 2**32 and 0 <= event['drm_sec'] < 2**32
                and 0 <= event['drm_usec'] < 1000000 and event['result'] == 0):
            rejected_ids.append(list(key))
            continue
        event = dict(event)
        event['kernel_us'] = event['drm_sec'] * 1000000 + event['drm_usec']
        accepted.append(event)

    windows, anomalies = [], []
    for pid in sorted({e['pid'] for e in accepted}):
        events = sorted((e for e in accepted if e['pid'] == pid), key=lambda e: e['id'])
        all_deltas = [b['kernel_us'] - a['kernel_us'] for a, b in zip(events, events[1:])]
        seq_steps = [(b['drm_seq'] - a['drm_seq']) & 0xffffffff for a, b in zip(events, events[1:])]
        if (any(d <= 0 for d in all_deltas) or any(not 0 < d < 2**31 for d in seq_steps)
                or any(e['kernel_us'] < e['submit_us'] or e['kernel_us'] > e['callback_us'] for e in events)):
            anomalies.append(dict(pid=pid, reason='inconsistent callback clock/sequence ordering'))
            continue
        clients = [e for e in events if e['origin'] == 'client']
        if len(clients) < 2:
            continue
        intervals = [b['kernel_us'] - a['kernel_us'] for a, b in zip(clients, clients[1:])]
        windows.append(dict(pid=pid, completed=len(clients), start_kernel_us=clients[0]['kernel_us'],
                            end_kernel_us=clients[-1]['kernel_us'],
                            observed_completion_hz=(len(clients) - 1) * 1000000 / sum(intervals),
                            interval_min_us=min(intervals), interval_median_us=statistics.median(intervals),
                            interval_max_us=max(intervals),
                            refresh_steps=[(b['drm_seq'] - a['drm_seq']) & 0xffffffff
                                           for a, b in zip(clients, clients[1:])]))
    return dict(completed_client=sum(e['origin'] == 'client' for e in accepted),
                completed_cursor=sum(e['origin'] == 'cursor' for e in accepted),
                client_windows=windows, ordering_anomalies=anomalies,
                rejected_lines=rejected_lines, rejected_submission_ids=rejected_ids,
                record_limit_observed=limited, logging_error_observed=b'NATIVE_PRESENT043_LOG_ERROR' in raw,
                stable_120fps_verified=False, unique_visual_content_verified=False,
                sustained_workload_verified=False, thermal_clocks_verified=False,
                physical_board_test=False,
                scope='Bounded callback samples, trace UID field only; not identity attestation. '
                      'Initial modesets excluded; cursor events are not client frames. '
                      'Refresh steps are not proof of missed demanded frames. '
                      'Unflushed tails/lost records and periods outside the trace are unknown.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    result = analyze(raw)
    result.update(input=str(args.input), input_sha256=hashlib.sha256(raw).hexdigest())
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
