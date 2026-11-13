"""Reference ashmem must target only the isolated graphics kernel."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class AshmemIntegration(unittest.TestCase):
    def test_builder_matches_virtual_kernel_without_loading(self):
        path = HERE / 'build-original-graphics-ashmem-001.py'
        self.assertTrue(path.exists(), 'missing matching virtual ashmem build')
        payload = runpy.run_path(str(path))['payload']
        for text in ('original-graphics-kernel-002/out', 'CONFIG_ARM64_4K_PAGES=y',
                     "s.replace('mm_page_size(desc->mm)', 'PAGE_SIZE')",
                     'Module.symvers', 'reference_sources_unchanged', 'modinfo'):
            self.assertIn(text, payload)
        self.assertNotIn('insmod', payload)
        self.assertNotIn('modprobe', payload)
        self.assertNotIn('ssh ', payload)
        compile(payload, 'offline-graphics-ashmem', 'exec')

    def test_independent_verifier_checks_packaged_module_and_real_device(self):
        verifier = HERE / 'verify-original-graphics-boot-074.py'
        self.assertTrue(verifier.exists(), 'missing independent ashmem verification')
        module = runpy.run_path(str(verifier))
        source = module['source']
        self.assertIn("entries['graphics-ashmem.ko'][1]", source)
        self.assertIn('ashmem_module_archive_verified', source)
        self.assertIn('observed_ashmem_loads', source)
        self.assertIn('observed_registered_ashmem_devices', source)
        self.assertIn('kernel_registered=1', source)
        compile(source, 'offline-ashmem-verifier-074', 'exec')

    def test_image_only_build_uses_real_kernel_symbol_table(self):
        path = HERE / 'build-original-graphics-ashmem-002.py'
        self.assertTrue(path.exists(), 'missing Image-only symbol-table adapter')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('vmlinux.symvers', payload)
        self.assertIn('KBUILD_EXTRA_SYMBOLS=', payload)
        self.assertIn('original-graphics-ashmem-002', payload)
        self.assertNotIn('insmod', payload)
        compile(payload, 'offline-graphics-ashmem-002', 'exec')

    def test_module_preparation_is_confined_to_a_copy(self):
        path = HERE / 'build-original-graphics-ashmem-003.py'
        self.assertTrue(path.exists(), 'missing isolated module-preparation adapter')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn("build_k = out / 'kernel-build'", payload)
        self.assertIn("'cp', '-a', '--reflink=auto'", payload)
        self.assertIn("'modules_prepare'", payload)
        self.assertIn("build_k / 'scripts/module.lds'", payload)
        self.assertNotIn('KBUILD_MODPOST_WARN', payload)
        self.assertNotIn('insmod', payload)

    def test_copied_kbuild_cannot_redirect_preparation_to_original_output(self):
        path = HERE / 'build-original-graphics-ashmem-004.py'
        self.assertTrue(path.exists(), 'missing explicit Kbuild O= isolation')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn("str(k.parent / 'linux'), 'O=' + str(build_k)", payload)
        self.assertNotIn("'-C', str(build_k)", payload)
        compile(payload, 'offline-graphics-ashmem-004', 'exec')

    def test_genuine_module_is_loaded_only_inside_guarded_guest(self):
        fixture = HERE / 'prepare-baremetal-sdk-original-init-074.py'
        runner = HERE / 'run-baremetal-sdk-original-init-074.py'
        self.assertTrue(fixture.exists(), 'missing guest-only ashmem integration')
        self.assertTrue(runner.exists(), 'missing ashmem integration runner')
        source = runpy.run_path(str(fixture))['source']
        main = source.index('int main(')
        self.assertLess(source.index('dummy-virt', main), source.index('graphics_ashmem_074();', main))
        self.assertLess(source.index('graphics_ashmem_074();', main), source.index('struct kernel_node', main))
        self.assertIn('SYS_finit_module', source)
        self.assertIn('/sys/class/misc/ashmem/dev', source)
        self.assertIn('S_ISCHR', source)
        payload = runpy.run_path(str(runner))['payload']
        self.assertIn('951e58dceffa3bc00abeab793b4dcbd8d846644d08524e5128aaff7f2c6c493d', payload)
        self.assertIn("add('graphics-ashmem.ko'", payload)
        self.assertIn('readonly=on', payload)
        self.assertIn('original-graphics-egl-009', payload)
        self.assertNotIn('ssh ', payload)


if __name__ == '__main__':
    unittest.main()
