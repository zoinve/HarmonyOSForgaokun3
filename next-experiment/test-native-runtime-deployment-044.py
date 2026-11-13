"""Offline deployment guards, not operational script discovery."""
from pathlib import Path
import ast
import runpy
import unittest

HERE = Path(__file__).parent
SHA = '1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1'


class DeploymentTests(unittest.TestCase):
    def load(self, name):
        path = HERE / name
        self.assertTrue(path.exists(), f'missing fresh {name}')
        return runpy.run_path(str(path))

    def test_read_only_fresh_inventory(self):
        s = self.load('audit-native-efi-space-044.py')['source']
        compile(s, 'inventory044-offline', 'exec')
        self.assertIn('native-presentation-044-efi-inventory.json', s)
        self.assertIn('screenoff_timer_active_enabled=True', s)
        self.assertNotIn('set-oneshot', s)

    def test_inert_stage_requires_audited_three_member_overlay(self):
        s = self.load('stage-native-original-graphics-boot-044.py')['source']
        compile(s, 'stage044-offline', 'exec')
        self.assertIn('native-original-graphics-boot-044', s)
        self.assertIn(SHA, s)
        self.assertIn("'native-target/bootstrap'", s)
        self.assertIn('native_boot_attempted', s)

    def test_installation_preserves_reserve_and_does_not_select(self):
        s = self.load('install-native-presentation-044.py')['source']
        compile(s, 'install044-offline', 'exec')
        ast.parse(s)
        self.assertIn('len(data)==699477', s)
        self.assertIn(SHA, s)
        self.assertIn('64*1024*1024+65536', s)
        self.assertIn("retired['files']", s)
        self.assertIn('artifact_table', s)
        self.assertIn('native-presentation-044-efi-inventory.json', s)
        self.assertNotIn('set-oneshot', s)
        self.assertNotIn("'reboot'", s)


if __name__ == '__main__':
    unittest.main()
