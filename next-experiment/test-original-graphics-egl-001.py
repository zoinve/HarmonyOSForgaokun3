"""Offline checks only; never start a guest or rerun an operational build."""
import pathlib
import runpy
import unittest

HERE = pathlib.Path(__file__).resolve().parent


class EglProviderSafety(unittest.TestCase):
    def test_scoped_reference_bridge_and_mesa_only(self):
        script = HERE / 'build-original-graphics-egl-001.py'
        self.assertTrue(script.exists(), 'EGL provider builder missing')
        source = runpy.run_path(str(script))['payload']
        compile(source, str(script), 'exec')
        for text in ['egl_window_bridge.cpp', 'ohos-platform-cxx',
                     '--no-undefined', 'libEGL.so.1', 'libgallium-25.0.1.so',
                     'original_images_unchanged', 'reference_files_unchanged',
                     'runtime_executed=False', 'harmony-mesa', 'S_ISLNK',
                     'libc.so.6', 'unresolved_dependencies']:
            self.assertIn(text, source)
        for text in ['setenforce', 'ssh ', 'setuid(', 'sandbox', 'mount(']:
            self.assertNotIn(text, source)

    def test_separate_ndk_mesa_runtime_not_platform_replacement(self):
        script = HERE / 'build-original-graphics-egl-002.py'
        self.assertTrue(script.exists(), 'Scoped NDK runtime adapter missing')
        source = runpy.run_path(str(script))['payload']
        compile(source, str(script), 'exec')
        self.assertIn("'libc++_shared.so'", source)
        self.assertIn('original-graphics-egl-002', source)
        self.assertIn('legacy_mesa_runpath_alias', source)
        self.assertIn("'libc++.so'", source)

    def test_guest_system_overlay_keeps_original_services(self):
        script = HERE / 'prepare-baremetal-sdk-original-init-054.py'
        self.assertTrue(script.exists(), 'Original-init EGL overlay missing')
        source = runpy.run_path(str(script))['source']
        for text in ['lowerdir=/run/system-lower', 'MS_BIND | MS_REMOUNT | MS_RDONLY',
                     '/graphics-egl/', 'harmony-mesa/libc++_shared.so',
                     'O_EXCL | O_NOFOLLOW', 'lab-softpipe-167',
                     'service_credentials_unmodified=1', 'libGLESv3_impl.so']:
            self.assertIn(text, source)
        for text in ['setuid(', 'setcon(', 'LD_LIBRARY_PATH', 'sandbox=0']:
            self.assertNotIn(text, source)

    def test_run_uses_modern_gpu_and_hash_pinned_scoped_bundle(self):
        script = HERE / 'run-baremetal-sdk-original-init-054.py'
        self.assertTrue(script.exists(), 'Full-graph EGL run adapter missing')
        source = runpy.run_path(str(script))['payload']
        compile(source, str(script), 'exec')
        for text in ['virtio-mmio.force-legacy=false', 'readonly=on',
                     'original-graphics-egl-002/result.json', 'graphics-egl/',
                     "sha(p)==row['sha256']", "len(egl['files'])==9",
                     'baremetal-sdk-original-init-054', 'GRAPHICS054_']:
            self.assertIn(text, source)

    def test_bounded_observer_accepts_real_partial_sample_count(self):
        module = runpy.run_path(str(HERE / 'verify-original-graphics-boot-053.py'))
        function = module.get('verify_mode_samples')
        self.assertTrue(callable(function), 'Bounded sample validator missing')
        raw = b''.join(('GRAPHICS050_SELINUX sample=%d enforce=0\n' % i).encode() for i in range(23))
        self.assertEqual(function(raw, b'GRAPHICS050_'), 23)
        with self.assertRaises(AssertionError):
            function(raw.replace(b'enforce=0', b'enforce=1', 1), b'GRAPHICS050_')

    def test_egl_verifier_does_not_invent_allocator_mapping(self):
        source = runpy.run_path(str(HERE / 'verify-original-graphics-boot-054.py'))['source']
        self.assertIn('allocator_vdi_mapping_observed=', source)
        self.assertIn('/system/lib64/chipset-sdk-sp/libc++.so', source)
        self.assertTrue('re.escape(path.encode())' in source, 'C++ library paths must match literally')


if __name__ == '__main__':
    unittest.main()
