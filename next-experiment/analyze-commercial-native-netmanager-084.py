"""Correlate original DHCP, NetManager and OOBE evidence, separately from kernel state."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def analyze(text):
    def lines(pattern):
        return list(dict.fromkeys(line for line in text.splitlines() if re.search(pattern, line)))
    registrations = lines(r'netmanager/NetConnManager: RegisterNetSupplier service out, supplier\[\d+ wlan0\] netId\[\d+\]')
    defaults = lines(r'netmanager/NetConnManager: set default supplier\[\d+\]')
    ids = {re.search(r'supplier\[(\d+) wlan0\]', row).group(1) for row in registrations}
    matching = [row for row in defaults if re.search(r'supplier\[(\d+)\]', row).group(1) in ids]
    dhcp = lines(r'zz_l410_wifi_bridge/DhcpClientServiceImpl: DhcpIpv4ResultSuccess wlan0, 0,')
    oobe_default = lines(r'hwstartupguide/HwStartupGuide: InternetManager:hasDefaultNet: true$')
    probe = lines(r'netmanager/NetConnManager: https url detection result: success$')
    return dict(original_dhcp_ipv4_success_records=dhcp,
                original_netmanager_registration_records=registrations,
                original_netmanager_matching_default_records=matching,
                original_netmanager_link_update_completed_records=lines(r'netmanager/NetConnManager: UpdateNetLinkInfo service out\.'),
                original_netmanager_https_detection_success_records=probe,
                original_oobe_default_network_true_records=oobe_default,
                original_oobe_available_records=lines(r'hwstartupguide/HwStartupGuide: InternetManager:net available$'),
                original_oobe_validation_timeout_records=lines(r'hwstartupguide/HwStartupGuide: InternetManager:wait net validate time out\.'),
                original_oobe_creation_records=lines(r'hwstartupguide/HwStartupGuide: GuideHomeAbility:onCreate$'),
                original_sceneboard_oobe_start_records=lines(r'sceneboard/HOME: BaseOobeManager: start oobe$'),
                original_dhcp_completion_proven=bool(dhcp),
                original_netmanager_default_selection_proven=bool(matching),
                original_oobe_default_network_visibility_proven=bool(matching and oobe_default),
                https_success_is_original_service_report_not_independent_curl_verification=bool(probe),
                independent_dns_and_https_verification_proven=False,
                oobe_completed_proven=False, desktop_visible_interaction_proven=False,
                missing_bridge_status_files_not_equivalent_to_failed_publication=True)


def main():
    folder = ROOT / 'reports/commercial61-native-084'
    source = folder / 'runtime-evidence/raw/interactive-hilog030.log'
    blob = source.read_bytes()
    result = analyze(blob.decode(errors='replace'))
    result.update(source_name=source.name, source_sha256=hashlib.sha256(blob).hexdigest(),
                  complements_phase_only_network_analysis_without_overwriting_it=True)
    with (folder / 'native-service-network-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
