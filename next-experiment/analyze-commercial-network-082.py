"""Distinguish a PHY move from verified target visibility and connectivity."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    def unique(pattern):
        return list(dict.fromkeys(re.findall(pattern, text, re.MULTILINE)))

    moves = unique(r'^NETWORK082_PHY_MIGRATION status=(-?\d+) association_requested=0$')
    joins = unique(r'^NETWORK082_NAMESPACE_JOINED pid=\d+ source_inode=\d+ target_inode=\d+ connectivity_not_inferred=1$')
    observed = []
    for block in re.finditer(r'^PHASE_BEGIN wifi-target-observe082\n(.*?)^PHASE_END wifi-target-observe082 status=(-?\d+)\s*$', text, re.MULTILINE | re.DOTALL):
        content, status = block.groups()
        if status != '0':
            continue
        join = re.search(r'^NETWORK082_NAMESPACE_JOINED pid=(\d+) source_inode=(\d+) target_inode=(\d+) connectivity_not_inferred=1$', content, re.MULTILINE)
        if not join or join.group(2) == join.group(3):
            continue
        interfaces = re.findall(r'^\s+Interface ([^\s]+)\s*$', content[join.end():], re.MULTILINE)
        for name in interfaces:
            row = dict(pid=int(join.group(1)), interface=name, namespace_inode=int(join.group(3)))
            if row not in observed:
                observed.append(row)
    return dict(migration_status_records=moves, namespace_join_records=joins,
                target_iw_verified_interfaces=observed,
                target_namespace_wireless_visibility_proven='0' in moves and bool(observed),
                target_observer_status_records=unique(r'^PHASE_END wifi-target-observe082 status=(-?\d+)$'),
                namespace_failure_records=unique(r'^NETWORK082_(?:NAMESPACE_OPEN_FAILED|NAMESPACE_REFUSED|SETNS_FAILED|IW_EXEC_FAILED).*$'),
                target_exit_records=unique(r'^COMMERCIAL082_TARGET_EXIT .*$'),
                target_timeout_recovered='COMMERCIAL082 target_timeout=1' in text,
                association_requested=False, harmony_default_network_proven=False,
                oobe_completed_proven=False, desktop_visible_interaction_proven=False)


def main():
    folder = ROOT / 'reports/commercial61-native-082'
    paths = sorted((folder / 'runtime-evidence/raw').glob('phase-*.log'))
    assert paths, 'no recovered phase evidence'
    blob = paths[-1].read_bytes()
    result = analyze(blob.decode(errors='replace'))
    result.update(selected_cumulative_phase=paths[-1].name,
                  selected_phase_sha256=hashlib.sha256(blob).hexdigest(),
                  cumulative_snapshots_not_counted_as_repeated_operations=True)
    with (folder / 'network-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
