"""Offline gates for a mount-layout adaptation, not a fabricated SA profile."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent


class SystemBindTests(unittest.TestCase):
    def test_original_nodev_mount_flag_is_preserved(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-089.py'
        self.assertTrue(path.exists(), 'missing nodev-preserving fresh fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('mount(NULL, "/system", NULL, MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV, NULL)', source)
        self.assertIn('MS_RDONLY | MS_NODEV, "noload"', source)

    def test_system_is_real_readonly_bind_before_original_init(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-088.py'
        self.assertTrue(path.exists(), 'missing fresh mount-layout fixture')
        data = runpy.run_path(str(path))
        source = data['source']
        self.assertNotIn('symlink("/usr/system", "/system")', source)
        self.assertIn('mount("/usr/system", "/system", NULL, MS_BIND, NULL)', source)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY', source)
        self.assertIn('strcmp(system_real, "/system")', source)
        self.assertLess(source.index('readonly_image("sdk-system"'), source.index('original system readonly bind'))
        self.assertLess(source.index('original system readonly bind'), source.index('execve(arguments[0]'))
        self.assertIn('symlink("/system/etc", "/etc")', source)
        self.assertNotIn('setparam const.cust.config_dir_layer', source)
        self.assertNotIn('mkdir("/system/profile', source)
        compile(data['payload'], '<prepare088>', 'exec')

    def test_fresh_run_recovery_and_verifier_keep_original_checks(self):
        for name in ('run-baremetal-sdk-original-init-088.py', 'recover-original-audit-copy-088.py',
                     'verify-original-graphics-boot-088.py'):
            self.assertTrue((HERE / name).exists(), 'missing ' + name)
        run = runpy.run_path(str(HERE / 'run-baremetal-sdk-original-init-088.py'))['payload']
        self.assertIn('original-init-088/result.json', run)
        self.assertIn('readonly=on', run)
        self.assertIn('original-graphics-provider-005', run)
        self.assertIn('original-graphics-egl-009', run)
        self.assertNotIn('ssh ', run)
        recovery = runpy.run_path(str(HERE / 'recover-original-audit-copy-088.py'))['payload']
        self.assertIn('stat /graphics-audit-088.log', recovery)
        verify = runpy.run_path(str(HERE / 'verify-original-graphics-boot-088.py'))['source']
        self.assertIn('original-audit-copy-088', verify)
        self.assertIn('original_images_independent_hashes', verify)
        self.assertIn('physical_board_test=False', verify)
        for text in (run, recovery, verify):
            compile(text, '<fresh088>', 'exec')


if __name__ == '__main__':
    unittest.main()
