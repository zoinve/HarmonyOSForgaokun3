"""Offline gates for a longer observation of the unchanged original service graph."""
from pathlib import Path
import runpy
import unittest
import ast
import re

HERE = Path(__file__).resolve().parent


class LongObservationTests(unittest.TestCase):
    def test_verifier_checks_long_mode_sequence_without_claiming_readiness(self):
        path = HERE / 'verify-original-graphics-boot-067.py'
        self.assertTrue(path.exists(), 'missing longer observation verifier')
        source = runpy.run_path(str(path))['source']
        self.assertIn('readiness_verified=False', source)
        self.assertIn('extract_process_pids', source)
        tree = ast.parse(source)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == 'verify_mode_samples')
        scope = {'re': re}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<mode-test>', 'exec'), scope)
        raw = b''.join(b'GRAPHICS067_SELINUX sample=%d enforce=0\n' % i for i in range(48))
        self.assertEqual(scope['verify_mode_samples'](raw, b'GRAPHICS067_'), 48)
        with self.assertRaises(AssertionError):
            scope['verify_mode_samples'](raw.replace(b'sample=20 enforce=0', b'sample=20 enforce=1'), b'GRAPHICS067_')

    def test_observer_retains_credentials_and_adds_late_queries(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-067.py'
        self.assertTrue(path.exists(), 'missing longer original-service observer')
        source = runpy.run_path(str(path))['source']
        self.assertIn('sample < 48', source)
        self.assertIn('sample == 29', source)
        self.assertIn('sample == 41', source)
        self.assertIn('GRAPHICS067_', source)
        self.assertIn('"/system/bin/hilog", "-x", "-P"', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)

    def test_runner_changes_observation_bound_not_providers(self):
        path = HERE / 'run-baremetal-sdk-original-init-067.py'
        self.assertTrue(path.exists(), 'missing longer isolated runner')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('original-graphics-egl-009/result.json', payload)
        self.assertIn('harmony-sdk-qemu067-', payload)
        self.assertIn('timeout_seconds=360', payload)
        self.assertIn('stdout=f,stderr=subprocess.STDOUT,timeout=360', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn("'-smp','8'", payload)
        self.assertIn("'-m','4096'", payload)
        compile(payload, 'long-observation-run', 'exec')


if __name__ == '__main__':
    unittest.main()
