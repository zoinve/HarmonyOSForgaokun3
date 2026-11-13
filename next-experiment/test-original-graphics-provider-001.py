"""Explicit offline checks for the original-service VDI integration package."""
from pathlib import Path
import ast
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class ProviderSafety(unittest.TestCase):
    def test_modern_transport_required_by_original_gpu_driver(self):
        path = BASE / 'run-baremetal-sdk-original-init-053.py'
        self.assertTrue(path.exists(), 'modern virtio transport adapter missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        ast.parse(payload)
        self.assertIn("command+=['-global','virtio-mmio.force-legacy=false']", payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn('original-init-050/result.json', payload)
        self.assertIn('virtio-gpu-device', payload)

    def test_provider_trial_keeps_readonly_drives(self):
        payload = runpy.run_path(str(BASE / 'run-baremetal-sdk-original-init-050.py'), run_name='offline_generator')['payload']
        ast.parse(payload)
        self.assertIn("add('graphics-provider'", payload)
        self.assertIn('original-graphics-provider-002/result.json', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn('virtio-gpu-device', payload)
        self.assertNotIn('rendernode=', payload)

    def test_guest_provider_overlay_preserves_original_credentials(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-050.py'
        self.assertTrue(path.exists(), 'guest provider fixture missing')
        module = runpy.run_path(str(path), run_name='offline_generator')
        source = module['source']
        ast.parse(module['payload'])
        for expected in ['lowerdir=/run/vendor-lower', 'MS_BIND | MS_REMOUNT | MS_RDONLY',
                         'GRAPHICS050_DEVICE', '/sys/class/drm', 'service_credentials_unmodified=1']:
            self.assertIn(expected, source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertNotIn('LD_LIBRARY_PATH=', source)

    def test_archive_drm_symlink_resolves_to_real_elf(self):
        path = BASE / 'build-original-graphics-provider-002.py'
        self.assertTrue(path.exists(), 'cpio symlink correction missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        ast.parse(payload)
        self.assertIn("drm_link==b'libdrm.so.2.124.0'", payload)
        self.assertIn("libdrm.so.2.124.0'][1]", payload)
        self.assertIn("assert drm[:4]==b'\\x7fELF'", payload)

    def test_build_preserves_sdk_and_uses_platform_abi(self):
        path = BASE / 'build-original-graphics-provider-001.py'
        self.assertTrue(path.exists(), 'original-service provider builder missing')
        payload = runpy.run_path(str(path), run_name='offline_generator')['payload']
        ast.parse(payload)
        for expected in ['ohos-platform-cxx', 'buffer_vdi.cpp', 'composer.cpp',
                         '9c3ab7c3c83e074d0238814153752656c28b56202f833ad07f34b2cffd640912',
                         '--no-undefined', 'original_images_unchanged', 'reference_files_unchanged']:
            self.assertIn(expected, payload)
        self.assertNotIn('setenforce', payload)
        self.assertNotIn('ssh', payload)


if __name__ == '__main__':
    unittest.main()
