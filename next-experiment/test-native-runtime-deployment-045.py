"""Offline gates only; no discovery of operational experiment scripts."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent
SHA = '18d21887be15c02d15dde6b4fcaf8250e0dba1b755fcec3abd7a9c2511909d09'


class DeploymentTests(unittest.TestCase):
    def load(self, name):
        path = HERE / name
        self.assertTrue(path.exists(), f'missing fresh {name}')
        ns = runpy.run_path(str(path))
        compile(ns['source'], name, 'exec')
        return ns['source']

    def test_read_only_inventory_is_fresh(self):
        s = self.load('audit-native-efi-space-045.py')
        self.assertIn('native-presentation-045-efi-inventory.json', s)
        self.assertIn('screenoff_timer_active_enabled=True', s)
        self.assertNotIn('set-oneshot', s)

    def test_stage_requires_independent_capture_only_audit(self):
        s = self.load('stage-native-original-graphics-boot-045.py')
        self.assertIn('native-original-graphics-boot-045', s)
        self.assertIn(SHA, s)
        self.assertIn('bootstrap_source_changes_only_incremental_perf_capture', s)
        self.assertNotIn('bootstrap_source_changes_only_original_mnt_restore', s)
        self.assertIn("'native-target/bootstrap'", s)

    def test_installer_keeps_reserve_and_never_selects(self):
        s = self.load('install-native-presentation-045.py')
        self.assertIn('len(data)==701039', s)
        self.assertIn(SHA, s)
        self.assertIn('64*1024*1024+65536', s)
        self.assertIn('native-presentation-045-efi-inventory.json', s)
        self.assertIn('bootstrap_source_changes_only_incremental_perf_capture', s)
        self.assertIn('artifact_table', s)
        self.assertNotIn('set-oneshot', s)
        self.assertNotIn("'reboot'", s)


if __name__ == '__main__':
    unittest.main()
