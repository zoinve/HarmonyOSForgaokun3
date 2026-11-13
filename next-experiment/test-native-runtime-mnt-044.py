"""Offline source/archive gates; never run a native build or boot from tests."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class NativeRuntimeMountTests(unittest.TestCase):
    def test_only_original_mnt_setup_changes_inner_bootstrap(self):
        path = HERE / 'build-native-original-graphics-boot-044.py'
        self.assertTrue(path.exists(), 'missing fresh native mount candidate')
        ns = runpy.run_path(str(path))
        old = (HERE.parent / 'reports/native-original-graphics-boot-043/bootstrap.c').read_text()
        self.assertEqual(ns['restore_inner'](ns['inner']), old)
        main = ns['inner'][ns['inner'].index('int main(void)'):]
        self.assertLess(main.index('"Matebook E Go"'), main.index('native_runtime_mnt044();'))
        self.assertLess(main.index('native_runtime_mnt044();'), main.index('const char *sandboxes[]'))
        self.assertIn('mount("tmpfs", "/mnt", "tmpfs", MS_NOSUID, "mode=0755")', ns['inner'])
        self.assertIn('mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)', ns['inner'])
        self.assertIn("'native-target/bootstrap'", ns['payload'])
        self.assertIn("root/'native-presentation-043'", ns['payload'])
        self.assertNotIn('bootctl set-oneshot', ns['payload'])
        compile(ns['payload'], 'native044-build-offline', 'exec')

    def test_independent_full_archive_and_frozen_evidence_checks(self):
        path = HERE / 'verify-native-presentation-package-044.py'
        self.assertTrue(path.exists(), 'missing fresh independent mount candidate audit')
        p = runpy.run_path(str(path))['payload']
        self.assertIn('restore_inner', p)
        self.assertIn("kept={'init',vdi,'native-target/bootstrap'}", p)
        self.assertIn('original_images_independent_hashes=True', p)
        self.assertIn('older_native012_raw_files_verified=378', p)
        self.assertIn('native_boot_attempted=False', p)
        self.assertIn('existing_native043_raw_files_verified', p)
        compile(p, 'native044-audit-offline', 'exec')


if __name__ == '__main__':
    unittest.main()
