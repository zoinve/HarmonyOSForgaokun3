"""Offline checks only; do not execute the generated extraction payload."""
from pathlib import Path
import runpy
import unittest


class DirectoryUtilsAudit(unittest.TestCase):
    def test_original_directory_library_audit_is_read_only(self):
        path = Path(__file__).with_name('audit-original-directory-utils-001.py')
        self.assertTrue(path.is_file(), 'directory utility auditor missing')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, 'directory-utils-offline', 'exec')
        self.assertIn('original-directory-utils-001', payload)
        self.assertIn('/system/lib64/chipset-sdk-sp/libutils.z.so', payload)
        self.assertIn('assert sha(image)==before', payload)
        self.assertNotIn("'debugfs', '-w'", payload)
        self.assertNotIn('ssh', payload)


if __name__ == '__main__':
    unittest.main()
