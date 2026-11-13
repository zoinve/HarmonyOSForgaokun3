"""Offline checks only: preserve working layout and inspect genuine account logs."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent

class AccountObservationTests(unittest.TestCase):
    def test_canonical_layout_and_original_tools_without_audit_overhead(self):
        fixture = HERE / 'prepare-baremetal-sdk-original-init-090.py'
        self.assertTrue(fixture.exists(), 'missing account observation fixture')
        source = runpy.run_path(str(fixture))['source']
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', source)
        self.assertNotIn('symlink("/usr/system", "/system")', source)
        self.assertIn('GRAPHICS090_ACCOUNT_QUERY', source)
        self.assertIn('"/system/bin/hilog", "-z", "200", "-P"', source)
        self.assertIn('strncmp(text, "accountmgr ", 11)', source)
        for forbidden in ('AUDIT_ADD_RULE', 'fanotify_init', 'setuid(', 'setcon(', 'SystemWriteParam'):
            self.assertNotIn(forbidden, source)
        runner = HERE / 'run-baremetal-sdk-original-init-090.py'
        self.assertTrue(runner.exists(), 'missing numbered account runner')
        payload = runpy.run_path(str(runner))['payload']
        for expected in ('original-graphics-provider-005', 'original-graphics-egl-009', 'readonly=on'):
            self.assertIn(expected, payload)
        self.assertNotIn('audit=1', payload)
        compile(payload, '<offline-run090>', 'exec')

    def test_verifier_preserves_artifacts_and_real_business_results(self):
        path = HERE / 'verify-original-graphics-boot-090.py'
        self.assertTrue(path.exists(), 'missing account verifier')
        data = runpy.run_path(str(path))
        for expected in ('original_account_log_results', 'original_account_log_output',
                         'config_query_archive_verified=True', 'physical_board_test=False',
                         'GRAPHICS090_SYSTEM_BIND'):
            self.assertIn(expected, data['source'])
        compile(data['source'], '<offline-verify090>', 'exec')
        self.assertEqual(data['decode_commit_result']('Commit_rc_0'), 0)

if __name__ == '__main__':
    unittest.main()
