"""Offline configuration/safety checks; never execute an experimental builder."""
from pathlib import Path
import ast
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class BuildTests(unittest.TestCase):
    def test_isolated_real_software_driver_without_install_or_download(self):
        path = BASE / 'build-original-softpipe-001.py'
        self.assertTrue(path.exists(), 'missing isolated software Mesa builder')
        module = runpy.run_path(str(path))
        source = module['payload']
        ast.parse(source)
        for item in ('-Dgallium-drivers=softpipe', '--wrap-mode=nodownload',
                     'original-softpipe-001', 'exist_ok=False', '-j4',
                     "'original_build_unchanged'", "'driver_runtime_verified': False"):
            self.assertIn(item, source)
        for item in ("'install'", '--reconfigure', 'setenforce', 'ssh', 'setuid'):
            self.assertNotIn(item, source)
        self.assertIn('assert code_sections(old_gallium) == code_sections(packaged_gallium)', source)

    def test_original_service_trial_keeps_readonly_images_and_credentials(self):
        path = BASE / 'run-baremetal-sdk-original-init-061.py'
        self.assertTrue(path.exists(), 'missing original-service software Mesa trial')
        source = runpy.run_path(str(path))['payload']
        ast.parse(source)
        for item in ('original-init-qemu-061', 'original-init-059/result.json',
                     'original-graphics-egl-008/result.json', 'readonly=on',
                     'virtio-mmio.force-legacy=false', 'enforcing=0'):
            self.assertIn(item, source)
        self.assertNotIn('setuid', source)

    def test_bundle_changes_only_six_mesa_libraries(self):
        path = BASE / 'build-original-graphics-egl-008.py'
        self.assertTrue(path.exists(), 'missing coherent software Mesa bundle')
        source = runpy.run_path(str(path))['payload']
        ast.parse(source)
        for item in ('assert replaced == 6', "assert len(files) == 9",
                     "'libEGL_impl.so'", "'harmony-mesa/libc++_shared.so'",
                     'original-graphics-egl-007', 'original-softpipe-001',
                     'platform_libcxx_replaced=False', 'runtime_executed=False'):
            self.assertIn(item, source)

    def test_retry_uses_the_published_manifest_not_a_nonexistent_copy(self):
        path = BASE / 'run-baremetal-sdk-original-init-062.py'
        self.assertTrue(path.exists(), 'missing manifest-path correction')
        source = runpy.run_path(str(path))['payload']
        ast.parse(source)
        self.assertIn("local.parent/'original-graphics-egl-008/result.json'", source)
        self.assertNotIn("root/'original-graphics-egl-008/result.json'", source)
        self.assertIn('original-init-qemu-062', source)

    def test_verifier_reports_actual_context_results_without_presuming_success(self):
        path = BASE / 'verify-original-graphics-boot-062.py'
        self.assertTrue(path.exists(), 'missing actual-context verification')
        source = runpy.run_path(str(path))['source']
        ast.parse(source)
        for item in ("number='062', tag='059'", 'original-graphics-egl-008',
                     'actual_egl_context_created_pids', "'eglCreateContext'",
                     'prior_native_raw_files_verified'):
            self.assertIn(item, source)
        self.assertNotIn('assert actual_egl_context_created_pids', source)

    def test_targeted_original_hilog_keeps_original_service_and_bounds(self):
        path = BASE / 'prepare-baremetal-sdk-original-init-063.py'
        self.assertTrue(path.exists(), 'missing original-service targeted logs')
        source = runpy.run_path(str(path))['source']
        self.assertIn('"/system/bin/hilog", "-x", "-P", rs_pid_arg', source)
        self.assertIn('alarm(8)', source)
        self.assertIn('sample == 9 || sample == 13 || sample == 17', source)
        self.assertNotIn('setuid', source)
        self.assertNotIn('setcon(', source)

    def test_make_current_trace_preserves_real_call_and_return_logic(self):
        path = BASE / 'original-graphics-egl-trace-006.py'
        self.assertTrue(path.exists(), 'missing real make-current tracing')
        module = runpy.run_path(str(path))
        reference = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/egl_window_bridge.cpp').read_text()
        traced = module['adapt'](reference)
        self.assertIn('const EGLBoolean make_current_result = fn(', traced)
        self.assertIn('graphics_trace("eglMakeCurrent",', traced)
        self.assertEqual(reference, module['strip_trace'](traced))

    def test_resource_and_passive_dac_observation_keeps_original_security(self):
        path = BASE / 'run-baremetal-sdk-original-init-064.py'
        self.assertTrue(path.exists(), 'missing resource-bounded graphics observation')
        source = runpy.run_path(str(path))['payload']
        ast.parse(source)
        self.assertIn("'-smp','8','-m','4096'", source)
        self.assertIn('original-graphics-egl-009', source)
        parent_source = runpy.run_path(str(BASE / 'run-baremetal-sdk-original-init-063.py'))['payload']
        self.assertEqual(source.count('format=raw,readonly=on'), parent_source.count('format=raw,readonly=on'))
        fixture = runpy.run_path(str(BASE / 'prepare-baremetal-sdk-original-init-064.py'))['source']
        self.assertIn('GRAPHICS064_DRM_PERMISSIONS', fixture)
        self.assertIn('Gid:', fixture)
        self.assertIn('Groups:', fixture)
        self.assertNotIn('setuid', fixture)
        self.assertNotIn('setcon(', fixture)

    def test_actual_current_and_dac_evidence_is_not_a_success_substitute(self):
        path = BASE / 'verify-original-graphics-boot-064.py'
        self.assertTrue(path.exists(), 'missing real-current and DAC verification')
        source = runpy.run_path(str(path))['source']
        ast.parse(source)
        for item in ('actual_make_current_success_pids', 'observed_drm_permissions',
                     'observed_service_group_records', 'prior_native_raw_files_verified'):
            self.assertIn(item, source)
        self.assertNotIn('assert actual_make_current_success_pids', source)
        self.assertIn("stage_names = set(stage_names) | {'eglMakeCurrent'}", source)

    def test_crash_recovery_changes_only_a_new_scratch_clone(self):
        path = BASE / 'audit-original-graphics-crashes-064.py'
        self.assertTrue(path.exists(), 'missing independently preserved scratch recovery')
        source = runpy.run_path(str(path))['payload']
        ast.parse(source)
        self.assertIn("original.open('rb') as source, recovered.open('xb') as destination", source)
        self.assertIn("fsck_command=['e2fsck','-f','-p',str(recovered)]", source)
        self.assertIn('assert sha(original)==expected', source)
        self.assertNotIn("'debugfs','-w'", source)
        self.assertNotIn('mount', source)


if __name__ == '__main__':
    unittest.main()
