from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent
summarize = runpy.run_path(str(BASE / 'analyze-usb-storage-175.py'))['summarize']
FIXTURE = '''USB175_PROTECTED name=sda vid=346d pid=5678 major=8 minor=0 bytes=31666995200 before=0 after=1 kernel_flag_only=1 media_data_writes=0
NATIVE_ORIGINAL_START real_pid=485 original_pid_in_namespace=1 credentials_unmodified=1
USBSTORAGE174_BEGIN target=485 mono_ms=120000 read_only=1 service_acceptance_not_inferred=1
USBSTORAGE174_BLOCK name=sda vid=346d pid=5678 major=8 minor=0 sectors=61849600 ro=1 removable=1 partition=-1 target_dev_available=1 matching_target_nodes=0 node_scan_complete=1
USBSTORAGE174_BLOCK name=sda1 vid=346d pid=5678 major=8 minor=1 sectors=61845392 ro=1 removable=-1 partition=1 target_dev_available=1 matching_target_nodes=0 node_scan_complete=1
USBSTORAGE174_HELPER name=mount.ntfs executable_file_present=1 executed=0
USBSTORAGE174_FUSE target_node_present=1
USBSTORAGE174_END raw_blocks_opened=0 nodes_created=0 media_written=0
'''


class AnalysisTests(unittest.TestCase):
    def test_real_disk_identity_and_protection_not_file_access(self):
        result = summarize(FIXTURE)
        self.assertTrue(result['kernel_usb_disk_readonly_verified'])
        self.assertTrue(result['late_usb_sampling_observed'])
        self.assertFalse(result['original_file_manager_access_verified'])
        self.assertFalse(result['original_usb_service_device_list_verified'])
        self.assertEqual(result['samples'][0]['original_helpers']['mount.ntfs'], 1)

    def test_readonly_size_target_and_guard_ambiguity_fail_closed(self):
        cases = [FIXTURE.replace(' ro=1 ', ' ro=0 '),
                 FIXTURE.replace('target=485', 'target=486'),
                 FIXTURE.replace('bytes=31666995200', 'bytes=100'),
                 FIXTURE.splitlines()[0] + '\n' + FIXTURE]
        for text in cases:
            self.assertFalse(summarize(text)['kernel_usb_disk_readonly_verified'])

    def test_incomplete_sample_does_not_pass(self):
        self.assertFalse(summarize(FIXTURE.split('USBSTORAGE174_END')[0])['kernel_usb_disk_readonly_verified'])

    def test_node_presence_is_not_native_ui_acceptance(self):
        result = summarize(FIXTURE.replace('matching_target_nodes=0', 'matching_target_nodes=1'))
        self.assertTrue(result['any_matching_original_root_block_node_observed'])
        self.assertFalse(result['original_file_manager_access_verified'])
        self.assertTrue(result['node_search_bounds']['exhaustive_absence_not_inferred'])


if __name__ == '__main__':
    unittest.main()
