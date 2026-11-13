"""Offline checks for an independent, non-executing artifact audit."""
from pathlib import Path
import runpy
import unittest


class AuditTests(unittest.TestCase):
    def test_manifest_is_read_from_actual_builder_output(self):
        p = Path(__file__).with_name('verify-original-adreno-mesa-003.py')
        self.assertTrue(p.exists(), 'missing fresh audit with the actual manifest location')
        s = runpy.run_path(str(p))['payload']
        self.assertIn("manifest = project/'reports/original-adreno-mesa-002/result.json'", s)
        self.assertNotIn("manifest = work/'result.json'", s)
        self.assertIn('original-adreno-mesa-003-independent', s)
        compile(s, 'adreno-audit003-offline', 'exec')

    def test_fresh_read_only_audit_not_another_build_or_hardware_test(self):
        p = Path(__file__).with_name('verify-original-adreno-mesa-002.py')
        self.assertTrue(p.exists(), 'missing independent artifact audit')
        s = runpy.run_path(str(p))['payload']
        compile(s, 'adreno-independent-offline', 'exec')
        for text in ('source_guards', 'intro-buildoptions.json', 'ALLOW_KCMP',
                     'original_images', 'native-original-graphics-boot-041',
                     'target_code_executed=False', 'device_accessed=False'):
            self.assertIn(text, s)
        for text in ('ninja', 'meson setup', 'insmod', 'ssh ', '/dev/dri/'):
            self.assertNotIn(text, s)


if __name__ == '__main__':
    unittest.main()
