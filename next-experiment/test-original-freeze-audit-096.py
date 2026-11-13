"""Offline safety gate for extracting existing, genuine application freeze logs."""
from pathlib import Path
import runpy
import unittest


class FreezeAuditTests(unittest.TestCase):
    def test_extraction_cannot_rerun_guest_or_write_retained_filesystem(self):
        p = Path(__file__).with_name('audit-original-sceneboard-freezes-096.py')
        self.assertTrue(p.exists(), 'missing read-only original freeze extractor')
        ns = runpy.run_path(str(p))
        source = p.read_text()
        self.assertIn('debugfs', source)
        self.assertIn("'-R'", source)
        self.assertNotIn("'-w'", source)
        self.assertNotIn('e2fsck', source)
        self.assertNotIn('qemu-system', source)
        self.assertIn('hashlib.file_digest', source)
        self.assertIn("['after_sha256']", source)
        self.assertIn("open('xb')", source)
        self.assertTrue(callable(ns['main']))


if __name__ == '__main__':
    unittest.main()
