"""Offline safety tests; never execute an operational experiment here."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent
REF = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/composer.cpp')


class ComposerTraceTest(unittest.TestCase):
    def test_independent_verifier_records_actual_trace_without_assuming_hotplug(self):
        verifier = HERE / 'verify-original-graphics-boot-069.py'
        self.assertTrue(verifier.exists(), 'missing full composer trace verifier')
        source = runpy.run_path(str(verifier))['source']
        self.assertIn('original-graphics-provider-004', source)
        self.assertIn('actual_original_composer_trace', source)
        self.assertIn('hotplug_callback_returned', source)
        self.assertIn('378', source)
        compile(source, 'composer-trace-verifier-offline', 'exec')

    def test_guest_capture_and_runner_use_new_provider_without_identity_changes(self):
        prep = HERE / 'prepare-baremetal-sdk-original-init-069.py'
        runner = HERE / 'run-baremetal-sdk-original-init-069.py'
        self.assertTrue(prep.exists(), 'missing composer capture fixture')
        self.assertTrue(runner.exists(), 'missing composer capture runner')
        source = runpy.run_path(str(prep))['source']
        payload = runpy.run_path(str(runner))['payload']
        self.assertIn('"composer-", 9', source)
        self.assertIn('original-graphics-provider-004/result.json', payload)
        self.assertIn('original-graphics-egl-009/result.json', payload)
        self.assertIn('readonly=on', payload)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        compile(payload, 'composer-capture-runner-offline', 'exec')

    def test_trace_does_not_break_multiline_layer_setter_macro(self):
        helper = HERE / 'original-composer-trace-002.py'
        self.assertTrue(helper.exists(), 'missing macro-safe trace adapter')
        mod = runpy.run_path(str(helper))
        original = REF.read_text()
        traced = mod['adapt'](original)
        self.assertNotIn('composer_trace("entry_name")', traced)
        self.assertEqual(mod['strip_trace'](traced), original)

    def test_provider_build_keeps_original_service_and_platform_abi(self):
        builder = HERE / 'build-original-graphics-provider-003.py'
        self.assertTrue(builder.exists(), 'missing traced provider builder')
        payload = runpy.run_path(str(builder))['payload']
        self.assertIn('original-composer-trace-001.py', payload)
        self.assertIn('strip_trace', payload)
        self.assertIn('std::__h', payload)
        self.assertIn('--no-undefined', payload)
        self.assertIn('original_images_unchanged', payload)
        compile(payload, 'provider-trace-offline', 'exec')

    def test_reversible_trace_preserves_real_callback_and_initialization(self):
        helper = HERE / 'original-composer-trace-001.py'
        self.assertTrue(helper.exists(), 'missing reversible composer trace')
        mod = runpy.run_path(str(helper))
        original = REF.read_text()
        traced = mod['adapt'](original)
        self.assertEqual(mod['strip_trace'](traced), original)
        self.assertIn('callback(0, true, data);', traced)
        self.assertEqual(traced.count('callback(0, true, data);'), 1)
        self.assertIn('AuroraOpenDisplayDrm(&state.drm, 1)', traced)
        self.assertIn('O_NOFOLLOW', traced)
        self.assertIn('errno = saved;', traced)
        self.assertNotIn('setuid(', traced)
        self.assertNotIn('setcon(', traced)


if __name__ == '__main__':
    unittest.main()
