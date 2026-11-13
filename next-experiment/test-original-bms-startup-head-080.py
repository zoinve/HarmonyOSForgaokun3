"""Original early log query; no replacement BMS database or permissions."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class StartupHead(unittest.TestCase):
    def test_original_head_query_only(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-080.py'
        self.assertTrue(path.exists(), 'missing original early Foundation query')
        source = runpy.run_path(str(path))['source']
        self.assertIn('"/system/bin/hilog", "-a", "600", "-P", argument, NULL', source)
        self.assertNotIn('"/system/bin/hilog", "-z", "200", "-P", argument, NULL', source)
        self.assertNotIn('mkdir("/data/service/el1/public/bms', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)

    def test_runner_and_independent_verifier(self):
        runner = HERE / 'run-baremetal-sdk-original-init-080.py'
        verifier = HERE / 'verify-original-graphics-boot-080.py'
        self.assertTrue(runner.exists(), 'missing isolated startup query runner')
        self.assertTrue(verifier.exists(), 'missing independent startup query verifier')
        payload = runpy.run_path(str(runner))['payload']
        for text in ('original-init-qemu-080', 'original-init-080/result.json',
                     'readonly=on', 'original-graphics-egl-009',
                     'original-graphics-provider-005', 'graphics-ashmem.ko'):
            self.assertIn(text, payload)
        module = runpy.run_path(str(verifier))
        compile(module['source'], 'offline-original-bms-080', 'exec')
        self.assertIn('original_bms_startup_lines', module['source'])
        self.assertIn('foundation_query_command_errors', module['source'])
        self.assertEqual(module['decode_commit_result']('Commit_rc_0'), 0)


if __name__ == '__main__':
    unittest.main()
