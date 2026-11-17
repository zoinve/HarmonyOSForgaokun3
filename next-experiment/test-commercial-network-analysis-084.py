from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-network-084.py')))['analyze']


def phase(mode, output, status=0, pid=405):
    return (f'PHASE_BEGIN wifi-supplicant-{mode}084\n'
            f'NETWORK084_TARGET_CONTEXT pid={pid} net_inode=200 mnt_inode=201 pid_inode=202 root_verified=1 mode={mode} connectivity_not_inferred=1\n'
            f'{output}\nPHASE_END wifi-supplicant-{mode}084 status={status}\n')


def file(path, body):
    return f'NETWORK084_FILE_BEGIN path={path}\n{body}\nNETWORK084_FILE_END path={path} bytes={len(body)} complete_not_inferred=1\n'


STATE = ('NETWORK084_ADDRESS interface=wlan0 family=2 value=192.168.10.129 netmask=255.255.255.0 flags=4163\n' +
         file('/proc/net/route', 'wlan0 00000000 010AA8C0 0003 0 0 0 00000000') +
         file('/data/local/tmp/l410-wifi-compat-v2/netmanager-v4.status', 'stage=complete result=0 supplier=1001') +
         file('/data/local/tmp/l410-wifi-compat-v2/natural-control-v6.status', 'stage=dhcp-cache-complete result=0'))
SAMPLE = ('NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY\n' + phase('start', '') +
          'NETWORK084_START_RESULT status=0 credentials_supplied=1 association_requested=1\n' +
          phase('status', 'wpa_state=ASSOCIATING') + phase('status', 'wpa_state=COMPLETED') + phase('network', STATE))


class AnalysisTests(unittest.TestCase):
    def test_real_association_and_kernel_state_not_internet(self):
        result = analyze(SAMPLE)
        self.assertTrue(result['actual_association_proven'])
        self.assertTrue(result['kernel_ipv4_address_and_default_route_proven'])
        self.assertEqual(result['actual_ipv4_default_routes'][0]['gateway'], '192.168.10.1')
        self.assertTrue(result['original_bridge_publication_reported_success'])
        self.assertTrue(result['original_bridge_dhcp_reported_complete'])
        self.assertFalse(result['internet_reachability_proven'])
        self.assertFalse(result['oobe_completed_proven'])

    def test_failed_command_does_not_admit_state(self):
        self.assertFalse(analyze(SAMPLE.replace(phase('network', STATE), phase('network', STATE, status=1)))['kernel_ipv4_address_and_default_route_proven'])

    def test_other_context_not_admitted(self):
        self.assertFalse(analyze(SAMPLE.replace(phase('status', 'wpa_state=COMPLETED'), phase('status', 'wpa_state=COMPLETED', pid=999)))['actual_association_proven'])

    def test_linklocal_or_missing_route_not_connectivity(self):
        self.assertFalse(analyze(SAMPLE.replace('value=192.168.10.129', 'value=169.254.10.1'))['kernel_ipv4_address_and_default_route_proven'])
        self.assertFalse(analyze(SAMPLE.replace('010AA8C0 0003', '010AA8C0 0001'))['kernel_ipv4_address_and_default_route_proven'])

    def test_bridge_failure_not_published(self):
        self.assertFalse(analyze(SAMPLE.replace('stage=complete result=0', 'stage=complete result=-1'))['original_bridge_publication_reported_success'])

    def test_cumulative_duplicates_not_repeated_addresses(self):
        self.assertEqual(len(analyze(SAMPLE + SAMPLE)['actual_interface_addresses']), 1)


if __name__ == '__main__':
    unittest.main()
