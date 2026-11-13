"""Read-only inspection of the real loader, not an SA or permission replacement."""
from pathlib import Path
import runpy
import unittest


class ProfileAudit(unittest.TestCase):
    def test_genuine_binary_read_only(self):
        p = Path(__file__).with_name('audit-original-samgr-profiles-001.py')
        self.assertTrue(p.exists(), 'missing original profile loader audit')
        payload = runpy.run_path(str(p))['payload']
        self.assertIn('/system/bin/samgr', payload)
        self.assertIn('original-samgr-profiles-001', payload)
        self.assertIn('llvm-nm-19', payload)
        self.assertNotIn("'debugfs','-w'", payload)
        self.assertNotIn('setenforce', payload)
        compile(payload, 'offline-original-samgr-profile-audit', 'exec')


if __name__ == '__main__':
    unittest.main()
