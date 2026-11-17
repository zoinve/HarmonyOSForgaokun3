from pathlib import Path
import runpy
import unittest

inspect = runpy.run_path(str(Path(__file__).with_name('analyze-share-kernel-509.py')))['inspect']
SAMPLE = b'''PHASE_BEGIN wifi-supplicant-share-start086
NETWORK084_TARGET_CONTEXT pid=12 net_inode=100 mnt_inode=101 pid_inode=102 root_verified=1 mode=share-start connectivity_not_inferred=1
SHARE501_INTERFACE_ADD result=0 real_netdev_required=1
SHARE501_SUPPLICANT_START result=0 group_connected_not_inferred=1
SHARE501_PING pong=1 errno=0 transfer_verified=0
PHASE_END wifi-supplicant-share-start086 status=0
SHARE502_START_RESULT status=0 transfer_verified=0
N: Name="pmic_resin"
'''


class AnalysisTest(unittest.TestCase):
    def test_control_is_not_transfer_or_physical_key_acceptance(self):
        result = inspect(SAMPLE.splitlines())
        self.assertTrue(result['real_native_p2p_control_ready'])
        self.assertTrue(result['pmic_resin_input_lines'])
        self.assertFalse(result['huawei_share_file_transfer_verified'])
        self.assertFalse(result['physical_volume_down_verified'])

    def test_namespace_failure_timeout_and_interface_failure_are_not_success(self):
        for before, after in [(b'root_verified=1',b'root_verified=0'),
                              (b'086 status=0',b'086 status=124'),
                              (b'ADD result=0',b'ADD result=1')]:
            self.assertFalse(inspect(SAMPLE.replace(before,after).splitlines())['real_native_p2p_control_ready'])


if __name__ == '__main__':
    unittest.main()
