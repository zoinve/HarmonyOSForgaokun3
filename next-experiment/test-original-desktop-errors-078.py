"""Preserve original launch failures and query actual Foundation tail logs."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class DesktopErrors(unittest.TestCase):
    def test_actual_pid_tail_query_without_identity_changes(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-078.py'
        self.assertTrue(path.exists(), 'missing Foundation error observer')
        source = runpy.run_path(str(path))['source']
        self.assertIn('GRAPHICS078_FOUNDATION_QUERY', source)
        self.assertIn('"/system/bin/hilog", "-x", "-z", "200", "-P"', source)
        self.assertIn('sample == 24 || sample == 30 || sample == 41', source)
        self.assertIn('foundation_pid > 1', source)
        for forbidden in ('force-stop', 'setuid(', 'setcon(', 'setenforce('):
            self.assertNotIn(forbidden, source)

    def test_runner_keeps_same_original_desktop_requests(self):
        path = HERE / 'run-baremetal-sdk-original-init-078.py'
        self.assertTrue(path.exists(), 'missing isolated error observation runner')
        payload = runpy.run_path(str(path))['payload']
        for text in ('original-init-qemu-078', 'original-init-078/result.json',
                     'original-graphics-provider-005', 'original-graphics-egl-009',
                     'readonly=on', 'target==480'):
            self.assertIn(text, payload)
        compile(payload, 'offline-desktop-errors-078', 'exec')

    def test_verifier_preserves_real_query_status_and_output(self):
        path = HERE / 'verify-original-graphics-boot-078.py'
        self.assertTrue(path.exists(), 'missing Foundation response verifier')
        module = runpy.run_path(str(path))
        for name in ('original_foundation_log_queries', 'original_foundation_log_results',
                     'original_foundation_log_output'):
            self.assertIn(name, module['source'])
        raw = b'GRAPHICS078_STATE sample=17 pid=42 field=composer_remote bytes=-1 errno=13 base=0x1000 value=0x0 private_hash_specific_state=1\n'
        self.assertIsNone(module['parse_state_records'](raw)[0]['value'])
        compile(module['source'], 'offline-desktop-errors-verifier-078', 'exec')


if __name__ == '__main__':
    unittest.main()
