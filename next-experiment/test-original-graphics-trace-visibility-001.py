"""Offline checks only; never execute historical operations."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class VisibilityTests(unittest.TestCase):
    def test_trace_loader_and_directory_visibility(self):
        helper = HERE / 'original-graphics-egl-trace-002.py'
        self.assertTrue(helper.exists(), 'missing load/visibility trace adapter')
        data = runpy.run_path(str(helper))
        source = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/egl_window_bridge.cpp').read_text()
        traced = data['adapt'](source)
        self.assertEqual(data['strip_trace'](traced), source)
        self.assertIn('constructor', traced)
        self.assertIn('bridge_loaded', traced)
        self.assertIn('/data/graphics-trace', traced)
        self.assertNotIn('eglGetError();', traced.replace(source, ''))

    def test_fixture_reports_missing_directory(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-056.py'
        self.assertTrue(path.exists(), 'missing visibility fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('GRAPHICS056_TRACE_DIR', source)
        self.assertIn('/data/graphics-trace', source)
        self.assertIn('MS_RDONLY', source)
        self.assertNotIn('setuid(', source)

    def test_symbol_resolution_cannot_exhaust_result_budget(self):
        path = HERE / 'original-graphics-egl-trace-003.py'
        self.assertTrue(path.exists(), 'missing one-shot Mesa-library trace')
        data = runpy.run_path(str(path))
        source = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/egl_window_bridge.cpp').read_text()
        traced = data['adapt'](source)
        self.assertEqual(data['strip_trace'](traced), source)
        self.assertIn('mesa_logged.exchange(true', traced)
        self.assertLess(traced.index('mesa_logged.exchange(true'), traced.index('count.fetch_add'))


    def test_backend_alias_is_scoped_to_ram_overlay(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-059.py'
        self.assertTrue(path.exists(), 'missing scoped GBM backend path fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('symlink("harmony-mesa", "/system/lib64/lab-virgl883")', source)
        self.assertIn('GRAPHICS059_GBM_BACKEND_PATH', source)
        self.assertIn('RAM-only system graphics overlay', source)
        self.assertNotIn('setenv(', source)
        self.assertNotIn('setuid(', source)

    def test_backend_trial_verifier_reports_observed_stages(self):
        path = HERE / 'verify-original-graphics-boot-059.py'
        self.assertTrue(path.exists(), 'missing backend-path trial verifier')
        source = runpy.run_path(str(path))['source']
        compile(source, str(path), 'exec')
        self.assertIn("number='059', tag='059'", source)
        self.assertIn('original-graphics-egl-006', source)
        self.assertIn('GBM_BACKEND_PATH', source)
        self.assertIn('observed_display_stages', source)

    def test_gbm_failure_reports_real_loader_diagnostic_only_on_failure(self):
        path = HERE / 'original-graphics-egl-trace-005.py'
        self.assertTrue(path.exists(), 'missing failure-only loader diagnostics')
        data = runpy.run_path(str(path))
        source = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/egl_window_bridge.cpp').read_text()
        traced = data['adapt'](source)
        self.assertEqual(data['strip_trace'](traced), source)
        self.assertIn('if (!display.device)', traced)
        self.assertIn('dlerror()', traced)
        self.assertIn('EGL_TRACE_TEXT', traced)
        self.assertNotIn('RTLD_NOW | RTLD_GLOBAL', traced)
        self.assertEqual(traced.count('gbm_create_device(display.drm.fd)'), 1)

    def test_loader_trial_verifier_keeps_text_as_evidence(self):
        path = HERE / 'verify-original-graphics-boot-060.py'
        self.assertTrue(path.exists(), 'missing loader trial verifier')
        source = runpy.run_path(str(path))['source']
        compile(source, str(path), 'exec')
        self.assertIn("number='060', tag='059'", source)
        self.assertIn('real_loader_diagnostics', source)
        self.assertIn('EGL_TRACE_TEXT', source)

    def test_display_stage_diagnostics_keep_original_calls(self):
        path = HERE / 'original-graphics-egl-trace-004.py'
        self.assertTrue(path.exists(), 'missing display-stage diagnostics')
        data = runpy.run_path(str(path))
        source = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/egl_window_bridge.cpp').read_text()
        traced = data['adapt'](source)
        self.assertEqual(data['strip_trace'](traced), source)
        for name in ['drm_open_result', 'gbm_device', 'mesa_display']:
            self.assertIn('graphics_trace("' + name + '"', traced)
        self.assertEqual(traced.count('AuroraOpenDisplayDrm(&display.drm, 0)'), 1)
        self.assertEqual(traced.count('gbm_create_device(display.drm.fd)'), 1)


if __name__ == '__main__':
    unittest.main()
