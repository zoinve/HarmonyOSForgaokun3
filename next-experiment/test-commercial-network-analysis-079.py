from pathlib import Path
import runpy
import unittest

analyze = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-network-079.py')))['analyze']


class EvidenceTests(unittest.TestCase):
    def test_modprobe_success_is_not_connectivity(self):
        value = analyze('PHASE_END wifi-driver079 status=0\n')
        self.assertTrue(value['driver_command_exit_zero'])
        self.assertFalse(value['kernel_firmware_version_records'])
        self.assertFalse(value['harmony_default_network_proven'])

    def test_nonzero_not_success(self):
        self.assertFalse(analyze('PHASE_END wifi-driver079 status=124\n')['driver_command_exit_zero'])

    def test_repeated_snapshot_is_not_repeated_command(self):
        line = 'PHASE_END wifi-driver079 status=0\n'
        self.assertEqual(len(analyze(line * 3)['driver_phase_exit_records']), 1)

    def test_outer_interface_is_not_target_network(self):
        value = analyze('INTERFACE=/sys/class/net/lo\nINTERFACE=/sys/class/net/wlan0\n')
        self.assertEqual(value['outer_non_loopback_interface_records'], ['INTERFACE=/sys/class/net/wlan0'])
        self.assertFalse(value['interface_moved_to_target'])
        self.assertFalse(value['desktop_success_proven'])

    def test_firmware_and_error_observed_independently(self):
        value = analyze('ath11k_pci 0006:01:00.0: fw_version 0x11088c35\nath11k_pci 0006:01:00.0: firmware crashed\n')
        self.assertEqual(len(value['kernel_firmware_version_records']), 1)
        self.assertEqual(len(value['ath11k_error_records']), 1)


if __name__ == '__main__':
    unittest.main()
