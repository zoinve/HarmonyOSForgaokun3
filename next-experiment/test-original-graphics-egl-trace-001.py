"""Offline source transformation checks; no experiment launchers run."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent
REF = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/egl_window_bridge.cpp')


class TraceTests(unittest.TestCase):
    def test_trace_keeps_real_delegation_and_error_state(self):
        path = HERE / 'original-graphics-egl-trace-001.py'
        self.assertTrue(path.exists(), 'trace transformation missing')
        module = runpy.run_path(str(path))
        source = REF.read_text()
        traced = module['adapt'](source)
        self.assertIn('auto result = fn ? fn arguments : fallback;', traced)
        self.assertIn('local_error = code; return EGL_FALSE;', traced)
        self.assertIn('errno = saved;', traced)
        self.assertIn('O_NOFOLLOW', traced)
        self.assertNotIn('setuid(', traced)
        self.assertNotIn('setcon(', traced)
        self.assertNotIn('eglGetError() ==', traced)
        self.assertEqual(module['strip_trace'](traced), source)

    def test_trace_builder_keeps_original_images_and_reversibility(self):
        path = HERE / 'build-original-graphics-egl-003.py'
        self.assertTrue(path.exists(), 'trace builder missing')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, 'offline-builder', 'exec')
        self.assertIn("trace['strip_trace'](traced)==adapted", payload)
        self.assertIn('original_images', payload)
        self.assertIn('original-graphics-egl-003', payload)
        self.assertIn('reference source unmodified', payload)

    def test_guest_trace_capture_preserves_service_identity(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-055.py'
        self.assertTrue(path.exists(), 'trace capture fixture missing')
        source = runpy.run_path(str(path))['source']
        self.assertIn('O_NOFOLLOW', source)
        self.assertIn('GRAPHICS055_TRACE', source)
        self.assertIn('S_ISREG', source)
        self.assertIn('chmod("/run/graphics-trace", 01777)', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)

    def test_trace_run_stays_on_isolated_virtual_display(self):
        path = HERE / 'run-baremetal-sdk-original-init-055.py'
        self.assertTrue(path.exists(), 'trace runner missing')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, 'offline-runner', 'exec')
        self.assertIn('original-graphics-egl-003/result.json', payload)
        self.assertIn('virtio-mmio.force-legacy=false', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn('baremetal-sdk-original-init-055', payload)

    def test_verifier_requires_actual_trace_without_assuming_a_fix(self):
        path = HERE / 'verify-original-graphics-boot-055.py'
        self.assertTrue(path.exists(), 'trace evidence verifier missing')
        source = runpy.run_path(str(path))['source']
        compile(source, 'offline-verifier', 'exec')
        self.assertIn('egl_trace_capture_observed=bool(trace_records)', source)
        self.assertIn('original-graphics-egl-003', source)
        self.assertIn('desktop_verified=False', source)


if __name__ == '__main__':
    unittest.main()
