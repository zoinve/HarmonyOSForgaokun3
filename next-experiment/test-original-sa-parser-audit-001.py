from pathlib import Path
import runpy
import unittest


class OriginalParser(unittest.TestCase):
    def test_audit_never_executes_or_changes_original_parser(self):
        path = Path(__file__).with_name('audit-original-sa-parser-001.py')
        self.assertTrue(path.exists(), 'missing genuine SA parser audit')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('/system/lib64/platformsdk/libsamgr_common.z.so', payload)
        self.assertIn('original-sa-parser-001', payload)
        self.assertIn('target_code_executed=False', payload)
        self.assertNotIn("'debugfs','-w'", payload)
        compile(payload, 'offline-original-sa-parser-audit', 'exec')


if __name__ == '__main__':
    unittest.main()
