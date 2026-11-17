from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-native-netmanager-084.py')))['analyze']
SAMPLE = '''I C01565/zz_l410_wifi_bridge/DhcpClientServiceImpl: DhcpIpv4ResultSuccess wlan0, 0, opt:1
I C015B0/netmanager/NetConnManager: RegisterNetSupplier service out, supplier[1003 wlan0] netId[100]
I C015B0/netmanager/NetConnManager: set default supplier[1003].
I C015B0/netmanager/NetConnManager: UpdateNetLinkInfo service out.
I C015B0/netmanager/NetConnManager: https url detection result: success
I A00501/com.huawei.hmos.hwstartupguide/HwStartupGuide: InternetManager:hasDefaultNet: true
'''


class NativeServiceTests(unittest.TestCase):
    def test_matching_default_and_oobe_visibility(self):
        result = analyze(SAMPLE)
        self.assertTrue(result['original_dhcp_completion_proven'])
        self.assertTrue(result['original_netmanager_default_selection_proven'])
        self.assertTrue(result['original_oobe_default_network_visibility_proven'])
        self.assertFalse(result['independent_dns_and_https_verification_proven'])
        self.assertFalse(result['oobe_completed_proven'])

    def test_other_supplier_cannot_prove_wlan_default(self):
        result = analyze(SAMPLE.replace('set default supplier[1003]', 'set default supplier[2000]'))
        self.assertFalse(result['original_netmanager_default_selection_proven'])
        self.assertFalse(result['original_oobe_default_network_visibility_proven'])

    def test_registration_only_is_not_default(self):
        self.assertFalse(analyze(SAMPLE.split('set default supplier')[0])['original_netmanager_default_selection_proven'])

    def test_no_oobe_event_is_not_visibility_proof(self):
        self.assertFalse(analyze(SAMPLE.replace('hasDefaultNet: true', 'hasDefaultNet: false'))['original_oobe_default_network_visibility_proven'])

    def test_duplicate_logs_not_repeated_successes(self):
        self.assertEqual(len(analyze(SAMPLE + SAMPLE)['original_dhcp_ipv4_success_records']), 1)


if __name__ == '__main__':
    unittest.main()
