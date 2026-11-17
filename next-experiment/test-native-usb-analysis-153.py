from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-native-usb-153.py')))['summarize']


class OriginalBackendAnalysisTests(unittest.TestCase):
    def test_real_completion_is_not_service_or_ui_acceptance(self):
        result = summarize('''USB153_INIT status=0 backend_only=1
USB153_LIST count=1 backend_only=1 service_acceptance_not_inferred=1
USB153_DEVICE bus=5 address=2 node=/dev/bus/usb/005/002
USB153_END status=0 configuration_changed=0 interfaces_claimed=0 serials_read=0
USB153_PROBE_RESULT status=0 backend_only=1
''')
        self.assertTrue(result['original_backend_enumeration_completed'])
        self.assertFalse(result['usb_service_acceptance_verified'])
        self.assertFalse(result['usb_storage_file_access_verified'])

    def test_failure_and_missing_records(self):
        result = summarize('USB153_REFUSED reason=original_library_load_failed\nUSB153_PROBE_RESULT status=78 backend_only=1\n')
        self.assertFalse(result['original_backend_enumeration_completed'])
        result = summarize('USB153_INIT status=0 backend_only=1\nUSB153_LIST count=-3 backend_only=1 service_acceptance_not_inferred=1\n')
        self.assertFalse(result['original_backend_enumeration_completed'])

    def test_malformed_node_not_accepted(self):
        result = summarize('''USB153_INIT status=0 backend_only=1
USB153_LIST count=1 backend_only=1 service_acceptance_not_inferred=1
USB153_DEVICE bus=5 address=2 node=/dev/bus/usb/001/001
USB153_END status=0 configuration_changed=0 interfaces_claimed=0 serials_read=0
USB153_PROBE_RESULT status=0 backend_only=1
''')
        self.assertFalse(result['original_backend_enumeration_completed'])


if __name__ == '__main__':
    unittest.main()
