"""Classify independent original kernel observations, not network activation."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    def lines(pattern):
        return list(dict.fromkeys(line for line in text.splitlines() if re.search(pattern, line)))
    phases = {}
    for phase in ('wifi-power080', 'wifi-pci-power080', 'wifi-driver080', 'wifi-observation080'):
        phases[phase] = lines(r'^PHASE_END ' + re.escape(phase) + r' status=')
    return dict(phase_exit_records=phases,
                original_module_records=lines(r'^(?:pwrseq_qcom_wcn|pci_pwrctrl_pwrseq|ath11k_pci)\s'),
                phy_link_records=lines(r'^NETWORK080_PHY_OBSERVED=/sys/class/net/[^/]+/phy80211$'),
                observation_poll_records=lines(r'^NETWORK080_POLLS=\d+$'),
                observation_completed='NETWORK080_KERNEL_OBSERVATION_END_NOT_CONNECTIVITY' in text,
                pci_wifi_device_records=lines(r'(?i)pci .*\[17cb:1103\]'),
                firmware_identity_records=lines(r'ath11k_pci .*fw_version '),
                wifi_hardware_records=lines(r'ath11k_pci .*wcn6855'),
                firmware_or_driver_error_records=lines(r'(?i)ath11k.*(?:fail|error|timeout|crash)'),
                supplier_or_deferred_records=lines(r'(?:supplier:|NETWORK080_DEFERRED|deferred probe pending)'),
                explicit_phy_poll_exhausted='NETWORK080_POLLS=40' in text and 'NETWORK080_PHY_OBSERVED=' not in text,
                late_kernel_log_budget_refused='BUDGET_REFUSED phase=kernel-log' in text,
                target_timeout_recovered='COMMERCIAL080 target_timeout=1' in text,
                target_exit_records=lines(r'^COMMERCIAL080_TARGET_EXIT '),
                association_requested=False, target_interface_migration_requested=False,
                harmony_default_network_proven=False, oobe_completed_proven=False,
                desktop_visible_interaction_proven=False)


def main():
    report = ROOT / 'reports/commercial61-native-080'
    paths = sorted((report / 'runtime-evidence/raw').glob('phase-*.log'))
    assert paths, 'no recovered phase evidence'
    selected = paths[-1]
    blob = selected.read_bytes()
    result = analyze(blob.decode(errors='replace'))
    result.update(selected_cumulative_phase=selected.name,
                  selected_phase_sha256=hashlib.sha256(blob).hexdigest(),
                  cumulative_snapshots_not_counted_as_repeated_operations=True)
    with (report / 'network-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
