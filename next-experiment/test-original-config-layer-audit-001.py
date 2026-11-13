"""Offline gate for a read-only audit; never execute the generated payload."""
from pathlib import Path
import runpy
import unittest


class ConfigLayerAudit(unittest.TestCase):
    def test_original_library_is_only_extracted_and_inspected(self):
        path = Path(__file__).with_name('audit-original-config-layer-001.py')
        self.assertTrue(path.is_file(), 'read-only configuration library auditor missing')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, 'config-layer-audit-offline', 'exec')
        self.assertIn('original-config-layer-001', payload)
        self.assertIn('/system/lib64/chipset-sdk-sp/libconfigpolicy_util.z.so', payload)
        self.assertIn('debugfs', payload)
        self.assertIn('assert sha(image)==before', payload)
        self.assertNotIn("'debugfs', '-w'", payload)
        self.assertNotIn('ssh', payload)


if __name__ == '__main__':
    unittest.main()
