"""Correlate public mode, actual drawing boundaries and sparse output evidence."""
from collections import Counter
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / 'reports/commercial61-native-059'


def main():
    raw = ROOT / 'runtime-evidence'
    manifest = json.loads((raw / 'retrieval-manifest.json').read_text())
    for name, entry in manifest['files'].items():
        data = (raw / 'raw' / name).read_bytes()
        assert len(data) == entry['bytes']
        assert hashlib.sha256(data).hexdigest() == entry['sha256']
    hw = json.loads((ROOT / 'hwbreak-analysis.json').read_text())
    render = json.loads((ROOT / 'render-analysis.json').read_text())
    runtime = json.loads((ROOT / 'runtime-analysis.json').read_text())
    assert hw['run'] == render['run'] == runtime['run'] == manifest['run']
    first_flush = min(render['first_flush_guest_seconds'], default=None)
    events = [row['event'] for row in json.loads((BASE / 'reports/commercial-render-audit-059/result.json').read_text())['probes']]
    summary = {}
    for event in events:
        records = [r for r in hw['records'] if r['event'] == event]
        post = [r for r in records if first_flush is not None and r['ns'] >= first_flush * 1e9]
        summary[event] = dict(logged_samples=len(records),
            x0_histogram=dict(Counter(str(r['x0']) for r in records)),
            postflush_logged_samples=len(post),
            postflush_x0_histogram=dict(Counter(str(r['x0']) for r in post)),
            hardware_counter_total=sum(int(r['count']) for r in hw['final_counts'] if r['event'] == event),
            thread_ids=sorted(set(r['global_tid'] for r in records)))
    modes = [r['x0'] for r in hw['records'] if r['event'] == 'partial_mode_result']
    binary = (BASE / 'reports/commercial-oneway-audit-045/base.so').read_bytes()
    assert hashlib.sha256(binary).hexdigest() == '40bd0307b161f0f46ea82d3b08e3dca7819a5c4492066f0e462b8e172e2c50c8'
    # These literal addresses are the read-only PT_LOAD referenced by the audited getter.
    assert binary[0x2333ba:].split(b'\0', 1)[0] == b'rosen.uni.partialrender.enabled'
    assert binary[0x23adaa:].split(b'\0', 1)[0] == b'4'
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
        original_property_literals_verified=True,
        original_mode_reader_observed=bool(modes),
        all_logged_mode_reads_zero=bool(modes) and set(modes) == {0},
        events=summary, first_flush_guest_seconds=first_flush,
        last_composer_frame_seconds=render['last_frame_seconds'],
        postflush_composer_frames=render['postflush_frames'],
        postflush_sampled_nonblack_frames=render['postflush_sampled_nonblack_frames'],
        captures=runtime['captures'], lost_samples=hw['lost_samples'],
        suppressed_sample_log_lines=hw['suppressed_sample_log_lines'],
        observation_is_not_complete_thread_lifetime_coverage=True,
        actual_desktop_verified=False, interaction_verified=False)
    (ROOT / 'full-render-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != 'captures'}, indent=2))


if __name__ == '__main__':
    main()
