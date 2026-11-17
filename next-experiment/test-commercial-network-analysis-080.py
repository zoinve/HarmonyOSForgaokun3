from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-network-080.py')))['analyze']


class EvidenceTests(unittest.TestCase):
    def test_module_success_not_phy_or_connectivity(self):
        result = analyze('PHASE_END wifi-driver080 status=0\nath11k_pci 20480 0 - Live 0x0\n')
        self.assertEqual(len(result['original_module_records']), 1)
        self.assertFalse(result['phy_link_records'])
        self.assertFalse(result['harmony_default_network_proven'])

    def test_real_phy_and_firmware_do_not_prove_target_network(self):
        result = analyze('NETWORK080_PHY_OBSERVED=/sys/class/net/wlan0/phy80211\n[ 7.2] ath11k_pci 0006:01:00.0: fw_version 0x11088c35\n')
        self.assertEqual(len(result['phy_link_records']), 1)
        self.assertEqual(len(result['firmware_identity_records']), 1)
        self.assertFalse(result['target_interface_migration_requested'])
        self.assertFalse(result['oobe_completed_proven'])

    def test_exhausted_poll_is_explicit_negative_observation(self):
        result = analyze('NETWORK080_POLLS=40\nNETWORK080_KERNEL_OBSERVATION_END_NOT_CONNECTIVITY\nPHASE_END wifi-observation080 status=124\n')
        self.assertTrue(result['explicit_phy_poll_exhausted'])
        self.assertTrue(result['observation_completed'])

    def test_cumulative_duplicate_is_not_repeated_command(self):
        result = analyze('PHASE_END wifi-power080 status=0\n' * 3)
        self.assertEqual(len(result['phase_exit_records']['wifi-power080']), 1)

    def test_crash_and_firmware_seen_independently(self):
        result = analyze('ath11k_pci 0006:01:00.0: fw_version 0x1\nath11k_pci 0006:01:00.0: firmware crashed\n')
        self.assertEqual(len(result['firmware_identity_records']), 1)
        self.assertEqual(len(result['firmware_or_driver_error_records']), 1)
        self.assertFalse(result['desktop_visible_interaction_proven'])


if __name__ == '__main__':
    unittest.main()
