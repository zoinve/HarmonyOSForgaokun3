from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-network-082.py')))['analyze']
SAMPLE = '''NETWORK082_PHY_MIGRATION status=0 association_requested=0
PHASE_BEGIN wifi-target-observe082
NETWORK082_NAMESPACE_JOINED pid=404 source_inode=100 target_inode=200 connectivity_not_inferred=1
phy#0
    Interface wlan0
        ifindex 2
PHASE_END wifi-target-observe082 status=0
'''


class AnalysisTests(unittest.TestCase):
    def test_exact_target_visibility_not_connectivity(self):
        result = analyze(SAMPLE)
        self.assertTrue(result['target_namespace_wireless_visibility_proven'])
        self.assertEqual(result['target_iw_verified_interfaces'], [dict(pid=404, interface='wlan0', namespace_inode=200)])
        self.assertFalse(result['harmony_default_network_proven'])
        self.assertFalse(result['oobe_completed_proven'])

    def test_outer_interface_is_not_target_evidence(self):
        self.assertFalse(analyze('Interface wlan0\nNETWORK082_PHY_MIGRATION status=0 association_requested=0\n')['target_namespace_wireless_visibility_proven'])

    def test_failed_observer_does_not_prove_visibility(self):
        self.assertFalse(analyze(SAMPLE.replace('observe082 status=0', 'observe082 status=75'))['target_namespace_wireless_visibility_proven'])

    def test_same_namespace_is_rejected(self):
        self.assertFalse(analyze(SAMPLE.replace('target_inode=200', 'target_inode=100'))['target_namespace_wireless_visibility_proven'])

    def test_cumulative_duplicates_not_repeated_moves(self):
        result = analyze(SAMPLE + SAMPLE)
        self.assertEqual(result['migration_status_records'], ['0'])
        self.assertEqual(len(result['target_iw_verified_interfaces']), 1)


if __name__ == '__main__':
    unittest.main()
