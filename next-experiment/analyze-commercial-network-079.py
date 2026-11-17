"""Conservative kernel-network evidence classification, not desktop success."""
from pathlib import Path
import json
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    def lines(pattern):
        return list(dict.fromkeys(line for line in text.splitlines() if re.search(pattern, line)))
    driver_status = lines(r'^PHASE_END wifi-driver079 status=')
    firmware = lines(r'ath11k_pci .*fw_version ')
    interfaces = lines(r'^INTERFACE=/sys/class/net/(?!lo$).+')
    return dict(driver_phase_exit_records=driver_status,
                driver_command_exit_zero='PHASE_END wifi-driver079 status=0' in driver_status,
                kernel_firmware_version_records=firmware,
                outer_non_loopback_interface_records=interfaces,
                wlan_name_records=lines(r'ath11k_pci .*wlan[0-9]'),
                ath11k_error_records=lines(r'(?i)ath11k.*(?:fail|error|timeout|crash)'),
                late_kernel_log_budget_refused='BUDGET_REFUSED phase=kernel-log' in text,
                module_exit_does_not_establish_firmware_readiness=True,
                target_new_network_namespace=True,
                interface_moved_to_target=False,
                association_commanded=False,
                harmony_default_network_proven=False,
                oobe_completion_proven=False,
                desktop_success_proven=False)


def main():
    report = ROOT / 'reports/commercial61-native-079'
    raw = report / 'runtime-evidence/raw'
    paths = sorted(raw.glob('phase-*.log'))
    assert paths, 'runtime evidence not recovered'
    selected = paths[-1]
    blob = selected.read_bytes()
    text = blob.decode(errors='replace')
    result = analyze(text)
    result['selected_cumulative_phase'] = selected.name
    result['selected_phase_sha256'] = hashlib.sha256(blob).hexdigest()
    result['cumulative_snapshots_not_counted_as_repeated_operations'] = True
    with (report / 'network-analysis-revision2.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
