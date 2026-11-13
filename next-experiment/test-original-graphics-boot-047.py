"""Offline gates only: never discover or execute operational experiments."""
from pathlib import Path
import ast
import json
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class GraphicsBootSafety(unittest.TestCase):
    def test_virtual_display_trial_uses_pinned_isolated_kernel(self):
        path = BASE / 'run-baremetal-sdk-original-init-049.py'
        self.assertTrue(path.exists(), 'virtual display integration launcher missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        ast.parse(payload)
        self.assertIn('a75433f6f069d6607d3a34c461ae3723287d7ae67d45d72a68c7983f12a50136', payload)
        self.assertIn('original-graphics-kernel-002', payload)
        self.assertIn('virtio-gpu-device', payload)
        self.assertIn('gpu_attached=True', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertNotIn('rendernode=', payload)
        self.assertNotIn('ssh', payload)

    def test_missing_vendor_registration_import_preserves_services(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-048.py'
        self.assertTrue(path.exists(), 'original vendor import adapter missing')
        module = runpy.run_path(str(path), run_name='offline_generator')
        before = dict(imports_placeholder=True, services=[dict(name='render_service', uid='graphics', secon='u:r:render_service:s0')])
        before['import'] = ['/vendor/etc/init.${ohos.boot.hardware}.cfg']
        after = json.loads(module['patch_config'](json.dumps(before).encode()))
        expected = dict(before)
        expected['import'] = before['import'] + ['/vendor/etc/init/hdf_devhost.cfg']
        self.assertEqual(after, expected)
        with self.assertRaises(AssertionError):
            module['patch_config'](json.dumps(after).encode())
        ast.parse(module['payload'])

    def test_virtual_graphics_kernel_is_separate_from_board(self):
        path = BASE / 'build-original-graphics-kernel-001.py'
        self.assertTrue(path.exists(), 'virtual graphics kernel builder missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        ast.parse(payload)
        self.assertIn("'DRM_VIRTIO_GPU'", payload)
        self.assertIn("'DRM'", payload)
        self.assertIn('native_config_sha256', payload)
        self.assertIn('parent_kernel_unchanged', payload)
        self.assertIn('CONFIG_SECURITY_SELINUX', payload)
        self.assertNotIn('--disable\',\'SECURITY_SELINUX', payload)
        self.assertNotIn('bootctl', payload)

    def test_observed_i2c_promotions_are_explicitly_scoped(self):
        path = BASE / 'build-original-graphics-kernel-002.py'
        self.assertTrue(path.exists(), 'reviewed Kconfig dependency adapter missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        self.assertIn("'CONFIG_RTC_I2C_AND_SPI'", payload)
        self.assertIn("'CONFIG_I3C_OR_I2C'", payload)
        self.assertIn('CONFIG_SECURITY_SELINUX', payload)
        ast.parse(payload)

    def test_permissive_handoff_keeps_original_service_identities(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-047.py'
        self.assertTrue(path.exists(), 'permissive integration fixture missing')
        module = runpy.run_path(str(path), run_name='offline_generator')
        source = module['source']
        self.assertIn('enforcing=0', source)
        self.assertIn('SELINUX=permissive', source)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY', source)
        self.assertIn('execve(arguments[0], arguments, environment)', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertIn('GRAPHICS047_PROCESS', source)
        self.assertIn('GRAPHICS047_SELINUX', source)
        self.assertIn('composer_host', source)
        self.assertIn('render_service', source)
        self.assertIn('BLKROGET', source)
        ast.parse(module['payload'])

    def test_readonly_images_and_bounded_software_guest(self):
        path = BASE / 'run-baremetal-sdk-original-init-047.py'
        self.assertTrue(path.exists(), 'integration launcher missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        ast.parse(payload)
        self.assertIn("'tcg,thread=multi'", payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn("'-nic','none'", payload)
        self.assertIn('enforcing=0', payload)
        self.assertNotIn('enforcing=1', payload)
        self.assertIn('original_images_unchanged', payload)
        self.assertIn('timeout=90', payload)
        self.assertNotIn('ssh', payload)
        self.assertNotIn('set-oneshot', payload)


if __name__ == '__main__':
    unittest.main()
