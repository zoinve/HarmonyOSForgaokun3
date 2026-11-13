"""Original desktop requests must retain real authorization and results."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class DesktopRequest(unittest.TestCase):
    def test_only_normal_original_tool_requests(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-077.py'
        self.assertTrue(path.exists(), 'missing original desktop request fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('"/system/bin/bm", "dump", "-n", "com.ohos.sceneboard"', source)
        self.assertIn('"/system/bin/aa", "start", "-b", "com.ohos.sceneboard"', source)
        self.assertIn('"com.ohos.sceneboard.MainAbility", "-m", "pc_sceneboard"', source)
        self.assertIn('GRAPHICS077_DESKTOP_TOOL_END', source)
        self.assertIn('alarm(20)', source)
        for forbidden in ('force-stop', 'setuid(', 'setcon(', 'setenforce(', 'startupguide'):
            self.assertNotIn(forbidden, source)

    def test_bounded_isolated_capture_keeps_real_providers(self):
        path = HERE / 'run-baremetal-sdk-original-init-077.py'
        self.assertTrue(path.exists(), 'missing desktop request runner')
        payload = runpy.run_path(str(path))['payload']
        for name in ('original-init-qemu-077', 'original-init-077/result.json',
                     'original-graphics-provider-005', 'original-graphics-egl-009',
                     'readonly=on', 'graphics-ashmem.ko', 'target==480'):
            self.assertIn(name, payload)
        compile(payload, 'offline-desktop-077', 'exec')

    def test_verifier_records_requests_without_assuming_launch_success(self):
        path = HERE / 'verify-original-graphics-boot-077.py'
        self.assertTrue(path.exists(), 'missing original desktop response verifier')
        module = runpy.run_path(str(path))
        self.assertIn('original_desktop_tool_results', module['source'])
        self.assertIn('original_desktop_tool_output', module['source'])
        raw = b'GRAPHICS077_STATE sample=17 pid=42 field=composer_remote bytes=-1 errno=13 base=0x1000 value=0x0 private_hash_specific_state=1\n'
        self.assertIsNone(module['parse_state_records'](raw)[0]['value'])
        self.assertEqual(module['decode_commit_result']('Commit_rc_0'), 0)
        compile(module['source'], 'offline-desktop-verifier-077', 'exec')


if __name__ == '__main__':
    unittest.main()
