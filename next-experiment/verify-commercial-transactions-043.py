"""Verify completed evidence and original ELF binding without a target operation."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import subprocess


def verify(base):
    audit = base / 'reports/commercial-transaction-audit-043'
    summary = json.loads((audit / 'result.json').read_text())
    records = json.loads((audit / 'records.json').read_text())
    assert len(records) == summary['observer_records']
    assert dict(Counter(row['stage'] for row in records)) == summary['stages']
    binding = []
    for item in summary['original_libraries']:
        path = audit / item['name']
        assert path.stat().st_size == item['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        dynamic = subprocess.check_output(['aarch64-linux-gnu-readelf', '-d', str(path)], text=True)
        flags = [line.strip() for line in dynamic.splitlines() if '(FLAGS)' in line]
        binding.append(dict(name=item['name'], flags=flags,
                            symbolic=any('SYMBOLIC' in line for line in flags)))
    assert binding[0]['symbolic'], 'Recheck the original-library interception limitation'
    runtime = json.loads((base / 'reports/commercial61-native-042/runtime-analysis.json').read_text())
    preservation = json.loads((base / 'reports/commercial61-native-042/post-return-verification.json').read_text())
    assert runtime['run'] == summary['run'] and runtime['verified_files'] == 63
    assert runtime['configured_target_kill_observed']
    assert len(runtime['captures']) == 7
    assert all(capture['valid'] and capture['nonblack_pixels'] == 0 for capture in runtime['captures'])
    assert preservation['ubuntu_current_and_default']
    assert preservation['lab_partition_unmounted']
    assert preservation['custom_screenoff_timer_enabled_active']
    assert preservation['firmware_unchanged'] and preservation['old_manual_entry_retained']
    assert len(preservation['commercial_original_images_unchanged']) == 4
    scene = summary['processes']['3745']
    assert scene['values']['unirender_original_result'] == [1]
    assert scene['values']['hybrid_original_result'] == [0]
    assert scene['values']['director_rsroot_enter'] == [1]
    assert max(scene['values']['proxy_index_after']) == 34
    return dict(run=summary['run'], verified_files=63, verified_observer_records=len(records),
                bindings=binding, original_scene_root_observed=True,
                original_scene_transaction_index_reached=34,
                commit_interception_absence_does_not_prove_transaction_loss=True,
                desktop_verified=False, target_operations_performed=False)


if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    result = verify(base)
    path = base / 'reports/commercial-transaction-audit-043/independent-verification.json'
    with path.open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))
