"""Keep firmware/PHY/late-log evidence separate from actual target networking."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    def lines(pattern):
        return list(dict.fromkeys(line for line in text.splitlines() if re.search(pattern, line)))
    phases = {phase: lines(r'^PHASE_END ' + re.escape(phase) + r' status=') for phase in (
        'wifi-power081', 'wifi-pci-power081', 'wifi-qrtr081', 'wifi-driver081', 'wifi-observation081')}
    drain = lines(r'^NETWORK081_KMSG_DRAIN ')
    gaps = [line for line in drain if re.search(r'losses=[1-9]', line) or
            int(re.search(r'errno=(\d+)', line).group(1)) not in (0, 11)]
    return dict(phase_exit_records=phases,
                original_module_records=lines(r'^(?:pwrseq_qcom_wcn|pci_pwrctrl_pwrseq|qrtr_mhi|ath11k_pci)\s'),
                early_phy_link_records=lines(r'^NETWORK081_PHY_OBSERVED=/sys/class/net/[^/]+/phy80211$'),
                periodic_phy_link_records=lines(r'^NETWORK081_PHY_LINK name='),
                periodic_netif_records=lines(r'^NETWORK081_NETIF name='),
                mhi_driver_records=lines(r'/sys/bus/mhi/devices/.*/driver'),
                firmware_identity_records=lines(r'ath11k_pci .*fw_version '),
                wifi_hardware_records=lines(r'ath11k_pci .*wcn6855'),
                firmware_or_driver_error_records=lines(r'(?i)ath11k.*(?:fail|error|timeout|crash)'),
                kmsg_drain_records=drain,
                kmsg_gap_or_error_records=gaps,
                kmsg_open_failure_records=lines(r'^NETWORK081_KMSG_OPEN_FAILED '),
                observation_poll_records=lines(r'^NETWORK081_POLLS=\d+$'),
                observation_completed='NETWORK081_KERNEL_OBSERVATION_END_NOT_CONNECTIVITY' in text,
                target_exit_records=lines(r'^COMMERCIAL081_TARGET_EXIT '),
                target_timeout_recovered='COMMERCIAL081 target_timeout=1' in text,
                association_requested=False, target_interface_migration_requested=False,
                harmony_default_network_proven=False, oobe_completed_proven=False,
                desktop_visible_interaction_proven=False,
                kernel_record_absence_not_proof_of_runtime_absence=True)


def main():
    report = ROOT / 'reports/commercial61-native-081'
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
