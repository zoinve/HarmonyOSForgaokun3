from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-service-devices-152.py')))['summarize']


class ServiceAnalysisTests(unittest.TestCase):
    def test_private_nodes_not_outer_modes(self):
        result = summarize('''INPUTUSB148_USB_NODE stage=services_sample148 node=/dev/bus/usb/005/002 uid=0 gid=0 mode=600
SERVICEDEV152_BEGIN stage=test mono_ms=31000 read_only=1 input_events_read=0
SERVICEDEV152_ROOT stage=test pid=45 service=usb_host private_tmpfs=1
SERVICEDEV152_NODE stage=test pid=45 service=usb_host node=/dev/bus/usb/005/002 uid=3023 gid=3023 mode=660 char=1 major=189 minor=513 kernel_match=1
SERVICEDEV152_END stage=test permissions_changed=0 physical_acceptance_not_inferred=1
''')
        self.assertTrue(result['service_usb_nodes_observed'])
        self.assertEqual(result['latest_complete_sample']['nodes'][0]['gid'], 3023)
        self.assertFalse(result['usb_storage_file_access_verified'])

    def test_missing_nodes_preserved(self):
        result = summarize('''SERVICEDEV152_BEGIN stage=test mono_ms=31000 read_only=1 input_events_read=0
SERVICEDEV152_NODE_MISSING stage=test pid=45 service=usb_host node=/dev/bus/usb/005/002 errno=2 expected_major=189 expected_minor=513
SERVICEDEV152_END stage=test permissions_changed=0 physical_acceptance_not_inferred=1
''')
        self.assertFalse(result['service_usb_nodes_observed'])
        self.assertEqual(result['service_usb_nodes_missing'][0]['errno'], 2)

    def test_truncated_sample_not_latest_complete(self):
        result = summarize('SERVICEDEV152_BEGIN stage=test mono_ms=1 read_only=1 input_events_read=0\n')
        self.assertIsNone(result['latest_complete_sample'])
        self.assertFalse(result['service_usb_nodes_observed'])


if __name__ == '__main__':
    unittest.main()
