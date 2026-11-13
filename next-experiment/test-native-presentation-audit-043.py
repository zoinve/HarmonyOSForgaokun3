"""Offline gates for a nonexecuting artifact audit."""
from pathlib import Path
import runpy
import unittest


class AuditTests(unittest.TestCase):
    def test_independent_audit_keeps_old_artifacts_and_checks_reversal(self):
        path = Path(__file__).with_name('verify-native-presentation-043.py')
        self.assertTrue(path.exists(), 'missing independent presentation audit')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, '043-independent-offline', 'exec')
        self.assertIn("adapter['strip']", payload)
        self.assertIn("d['guarded_inputs']", payload)
        self.assertIn("retrieval['files']", payload)
        self.assertIn('target_code_executed=False', payload)
        self.assertIn('stable_120fps_verified=False', payload)
        self.assertNotIn('ssh ', payload)
        self.assertNotIn('pds_shell', payload)


if __name__ == '__main__':
    unittest.main()
