from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-network-083.py')))['analyze']


def phase(mode, output, status=0, pid=394):
    return (f'PHASE_BEGIN wifi-supplicant-{mode}083\n'
            f'NETWORK083_TARGET_CONTEXT pid={pid} net_inode=200 mnt_inode=201 pid_inode=202 root_verified=1 mode={mode} connectivity_not_inferred=1\n'
            f'{output}\nPHASE_END wifi-supplicant-{mode}083 status={status}\n')


SAMPLE = ('NETWORK083_TOOLS_VERIFIED_AND_EXTRACTED_RAM_ONLY\n' + phase('start', '') +
          'NETWORK083_START_RESULT status=0 credentials_supplied=0 association_requested=0\n' +
          phase('ping', 'PONG') + phase('scan', 'OK') +
          phase('scan_results', 'bssid / frequency / signal level / flags / ssid\n00:11:22:33:44:55\t2412\t-50\t[WPA2-PSK-CCMP][ESS]\ttest') +
          phase('status', 'wpa_state=DISCONNECTED'))


class AnalysisTests(unittest.TestCase):
    def test_real_control_and_bss_not_connectivity(self):
        result = analyze(SAMPLE)
        self.assertTrue(result['original_supplicant_started_proven'])
        self.assertTrue(result['target_control_ping_proven'])
        self.assertTrue(result['real_target_scan_results_proven'])
        self.assertEqual(result['real_bss_row_count'], 1)
        self.assertEqual(result['observed_wpa_states'], ['DISCONNECTED'])
        self.assertFalse(result['harmony_default_network_proven'])

    def test_exit_zero_with_fail_not_success(self):
        self.assertFalse(analyze(SAMPLE.replace('\nOK\n', '\nFAIL\n'))['real_target_scan_results_proven'])

    def test_other_namespace_context_is_not_admitted(self):
        self.assertFalse(analyze(SAMPLE.replace('mode=scan_results connectivity', 'mode=wrong connectivity'))['real_target_scan_results_proven'])
        self.assertFalse(analyze(SAMPLE.replace(phase('ping', 'PONG'), phase('ping', 'PONG', pid=999)))['real_target_scan_results_proven'])

    def test_empty_scan_is_not_invented(self):
        self.assertFalse(analyze(SAMPLE.replace('00:11:22:33:44:55', 'not-a-bss'))['real_target_scan_results_proven'])

    def test_failed_start_is_not_proof(self):
        self.assertFalse(analyze(SAMPLE.replace(phase('start', ''), phase('start', '', status=1)))['original_supplicant_started_proven'])

    def test_cumulative_duplicates_not_repeated_operations(self):
        self.assertEqual(analyze(SAMPLE + SAMPLE)['real_bss_row_count'], 1)


if __name__ == '__main__':
    unittest.main()
