"""Offline-only generation tests: never execute numbered operational payloads."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent


class AppSpawnObservation(unittest.TestCase):
    def test_real_daemon_and_tag_queries_keep_original_security(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-093.py'
        self.assertTrue(path.is_file())
        item = runpy.run_path(str(path))
        source = item['source']
        self.assertIn('GRAPHICS093_APPSPAWN_QUERY', source)
        self.assertIn('appspawn_pid', source)
        self.assertIn('"-P", argument', source)
        self.assertIn('"-T", "AppSpawn"', source)
        self.assertIn('original_tool=1', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertNotIn('sandbox=0', source)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', source)
        self.assertIn('16777216', source)
        compile(item['payload'], 'offline-093-build', 'exec')

    def test_trial_paths_and_independent_checks_are_fresh(self):
        for name, key in [('run-baremetal-sdk-original-init-093.py', 'payload'),
                          ('verify-original-graphics-boot-093.py', 'source')]:
            path = HERE / name
            self.assertTrue(path.is_file(), name)
            item = runpy.run_path(str(path))
            text = item[key]
            compile(text, 'offline-093-' + key, 'exec')
            self.assertEqual(text.count('baremetal-sdk-original-init-qemu-092'), 0)
            if key == 'payload':
                self.assertIn('original-graphics-provider-005', text)
                self.assertIn('original-graphics-egl-009', text)
                self.assertIn('for target in (120,360,480,600,650,660)', text)
                self.assertNotIn('ssh ', text)
            else:
                self.assertIn('original_appspawn_log_output', text)
                self.assertIn('original_images_independent_hashes', text)
                self.assertIn('independent_artifacts=json.loads(checked.stdout)', text)
                self.assertIn('physical_board_test=False', text)


if __name__ == '__main__':
    unittest.main()
