from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-network-081.py')))['analyze']


class EvidenceTests(unittest.TestCase):
    def test_module_success_not_network(self):
        value = analyze('PHASE_END wifi-qrtr081 status=0\nqrtr_mhi 16384 0 - Live 0x0\n')
        self.assertEqual(len(value['original_module_records']), 1)
        self.assertFalse(value['harmony_default_network_proven'])

    def test_late_records_recognized_without_desktop_inference(self):
        value = analyze('NETWORK081_PHY_LINK name=wlan0 target=../../phy0 connectivity_not_inferred=1\n6,12,5000000,-;ath11k_pci 0006:01:00.0: fw_version 0x1\n')
        self.assertEqual(len(value['periodic_phy_link_records']), 1)
        self.assertEqual(len(value['firmware_identity_records']), 1)
        self.assertFalse(value['desktop_visible_interaction_proven'])

    def test_eagain_is_not_gap_but_overrun_is(self):
        value = analyze('NETWORK081_KMSG_DRAIN records=2 bytes=40 selected=1 losses=0 errno=11 complete_not_inferred=1\nNETWORK081_KMSG_DRAIN records=1 bytes=20 selected=1 losses=1 errno=11 complete_not_inferred=1\n')
        self.assertEqual(len(value['kmsg_drain_records']), 2)
        self.assertEqual(len(value['kmsg_gap_or_error_records']), 1)

    def test_read_failure_is_gap(self):
        value = analyze('NETWORK081_KMSG_DRAIN records=0 bytes=0 selected=0 losses=0 errno=5 complete_not_inferred=1\n')
        self.assertEqual(len(value['kmsg_gap_or_error_records']), 1)

    def test_duplicate_snapshot_not_repeated_command(self):
        value = analyze('PHASE_END wifi-qrtr081 status=0\n' * 3)
        self.assertEqual(len(value['phase_exit_records']['wifi-qrtr081']), 1)


if __name__ == '__main__':
    unittest.main()
