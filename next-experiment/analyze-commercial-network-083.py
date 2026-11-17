"""Require real target context, control responses and BSS rows, not exit zero."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    phases = {}
    for block in re.finditer(r'^PHASE_BEGIN wifi-supplicant-(?P<mode>\w+)083\n(.*?)^PHASE_END wifi-supplicant-(?P=mode)083 status=(-?\d+)[ \t]*$', text, re.MULTILINE | re.DOTALL):
        mode, body, status = block.groups()
        context = re.search(r'^NETWORK083_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=(\d+) pid_inode=(\d+) root_verified=1 mode=' + re.escape(mode) + r' connectivity_not_inferred=1$', body, re.MULTILINE)
        if context:
            row = dict(status=int(status), pid=int(context.group(1)),
                       net_inode=int(context.group(2)), mnt_inode=int(context.group(3)),
                       pid_inode=int(context.group(4)), output=body[context.end():])
        else:
            row = dict(status=int(status), context_verified=False, output=body)
        phases[mode] = row

    def admitted(mode):
        row = phases.get(mode, {})
        start = phases.get('start', {})
        return row.get('status') == 0 and 'pid' in row and all(
            row.get(key) == start.get(key) for key in ('pid', 'net_inode', 'mnt_inode', 'pid_inode'))

    def exact_line(mode, line):
        return admitted(mode) and line in phases[mode]['output'].splitlines()

    start_ok = ('NETWORK083_TOOLS_VERIFIED_AND_EXTRACTED_RAM_ONLY' in text and admitted('start') and
                'NETWORK083_START_RESULT status=0 credentials_supplied=0 association_requested=0' in text)
    ping_ok = start_ok and exact_line('ping', 'PONG')
    scan_ok = ping_ok and exact_line('scan', 'OK')
    bss = []
    if scan_ok and admitted('scan_results'):
        for line in phases['scan_results']['output'].splitlines():
            if re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\s+\d+\s+-?\d+\s+\S+(?:[ \t]+.*)?', line):
                digest = hashlib.sha256(line.encode()).hexdigest()
                if digest not in bss:
                    bss.append(digest)
    states = []
    if admitted('status'):
        states = list(dict.fromkeys(re.findall(r'^wpa_state=(\S+)$', phases['status']['output'], re.MULTILINE)))
    return dict(tools_loaded_into_ram='NETWORK083_TOOLS_VERIFIED_AND_EXTRACTED_RAM_ONLY' in text,
                phase_status_records={mode: row['status'] for mode, row in phases.items()},
                verified_contexts={mode: {key: row[key] for key in ('pid', 'net_inode', 'mnt_inode', 'pid_inode')} for mode, row in phases.items() if 'pid' in row},
                original_supplicant_started_proven=start_ok,
                target_control_ping_proven=ping_ok, target_scan_request_acknowledged=scan_ok,
                real_bss_row_count=len(bss), real_bss_row_sha256=bss,
                real_target_scan_results_proven=scan_ok and bool(bss),
                observed_wpa_states=states,
                target_exit_records=list(dict.fromkeys(re.findall(r'^COMMERCIAL083_TARGET_EXIT .*$', text, re.MULTILINE))),
                target_timeout_recovered='COMMERCIAL083 target_timeout=1' in text,
                credentials_supplied=False, association_requested=False,
                harmony_default_network_proven=False, oobe_completed_proven=False,
                desktop_visible_interaction_proven=False)


def main():
    folder = ROOT / 'reports/commercial61-native-083'
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
