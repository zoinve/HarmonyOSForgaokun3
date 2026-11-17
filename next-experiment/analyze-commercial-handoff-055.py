"""Correlate register-only integration samples, retaining observation limits."""
from collections import Counter
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-055'
EVENTS = ['command_execute', 'screen_skip_result', 'worker_sync', 'worker_render']


def summarize(records, flush_ns):
    result = {}
    for event in EVENTS:
        all_rows = [row for row in records if row['event'] == event]
        after = [row for row in all_rows if row['ns'] >= flush_ns]
        item = dict(logged_samples=len(all_rows), logged_postflush_samples=len(after),
                    global_threads=sorted({row['global_tid'] for row in all_rows}),
                    postflush_global_threads=sorted({row['global_tid'] for row in after}),
                    first_seconds=min((row['ns'] for row in all_rows), default=0) / 1e9 if all_rows else None,
                    last_seconds=max((row['ns'] for row in all_rows), default=0) / 1e9 if all_rows else None)
        if event == 'screen_skip_result':
            # The audited instruction tests bit zero of w0, not pointer truthiness.
            item['sampled_skip_bits'] = dict(Counter(str(row['x0'] & 1) for row in all_rows))
            item['sampled_postflush_skip_bits'] = dict(Counter(str(row['x0'] & 1) for row in after))
        if event == 'command_execute':
            item['sampled_null_command_arguments'] = sum(row['x0'] == 0 for row in all_rows)
        result[event] = item
    return result


def main():
    hw = json.loads((ROOT / 'hwbreak-analysis.json').read_text())
    render = json.loads((ROOT / 'render-analysis.json').read_text())
    manifest = json.loads((ROOT / 'runtime-evidence/retrieval-manifest.json').read_text())
    assert hw['run'] == render['run'] == manifest['run']
    for name, row in manifest['files'].items():
        data = (ROOT / 'runtime-evidence/raw' / name).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    flush = render['first_flush_guest_seconds']
    assert flush, 'Cannot define a post-SceneBoard-flush interval without its actual log'
    flush_ns = int(Decimal(str(min(flush))) * 1000000000)
    coverage = {event: sorted({int(row['global_tid']) for row in hw['attachments'] if row['event'] == event})
                for event in EVENTS}
    counts = {}
    for event in EVENTS:
        rows = [row for row in hw['final_counts'] if row['event'] == event]
        counts[event] = dict(reported_counter_sum=sum(int(row['count']) for row in rows),
                             all_reported_counters_valid=bool(rows) and all(int(row['count_valid']) for row in rows),
                             reported_threads=len(rows))
    result = dict(run=hw['run'], verified_files=len(manifest['files']),
                  first_flush_seconds=min(flush), event_summary=summarize(hw['records'], flush_ns),
                  attached_thread_coverage=coverage, reported_counters=counts,
                  failures=hw['failures'], lost_samples=hw['lost_samples'],
                  malformed_records=hw['malformed_records'],
                  suppressed_sample_log_lines=hw['suppressed_sample_log_lines'],
                  instruction_pointer_mismatches=hw['instruction_pointer_mismatches'],
                  last_composer_frame_seconds=render['last_frame_seconds'],
                  postflush_composer_frames=render['postflush_frames'],
                  normal_target_timeout=hw['normal_target_timeout'], observer_stopped=hw['observer_stopped'],
                  periodic_attachment_is_not_complete_thread_lifetime_coverage=True,
                  command_callsite_is_not_command_success_or_gpu_submission=True,
                  worker_entry_is_not_frame_completion=True, private_objects_dereferenced=False,
                  actual_desktop_verified=False)
    (ROOT / 'handoff-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'attached_thread_coverage'}, indent=2))


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        assert all(row['first_seconds'] is None for row in summarize([], 10).values())
        rows = [dict(event='screen_skip_result', ns=9, global_tid=2, x0=0x100000001),
                dict(event='screen_skip_result', ns=10, global_tid=3, x0=2),
                dict(event='command_execute', ns=11, global_tid=2, x0=0x1000)]
        result = summarize(rows, 10)
        assert result['screen_skip_result']['sampled_skip_bits'] == {'1': 1, '0': 1}
        assert result['screen_skip_result']['sampled_postflush_skip_bits'] == {'0': 1}
        assert result['command_execute']['logged_postflush_samples'] == 1
        assert result['worker_sync']['logged_samples'] == 0
        print('PASS: empty coverage, exact flush boundary, audited w0 bit and non-null command register')
    else:
        main()
