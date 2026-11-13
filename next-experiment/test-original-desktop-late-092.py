"""Offline-only gates; never run numbered operational launchers as tests."""
import ast
from pathlib import Path
import re
import runpy
import unittest

HERE = Path(__file__).parent


class LateDesktopTests(unittest.TestCase):
    def load(self, name):
        path = HERE / name
        self.assertTrue(path.exists(), name)
        return runpy.run_path(str(path))

    def test_real_requests_are_later_without_bypasses(self):
        data = self.load('prepare-baremetal-sdk-original-init-092.py')
        source = data['source']
        self.assertIn('sample < 72', source)
        self.assertIn('if (sample == 45) graphics_desktop_tool_077(sample, 1);', source)
        self.assertIn('if (sample == 49) graphics_desktop_tool_077(sample, 2);', source)
        self.assertIn('16777216', source)
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', source)
        self.assertNotIn('force-stop', source)
        self.assertNotIn('setuid(', source)
        compile(data['payload'], '<prepare092>', 'exec')

    def test_numbered_volume_and_bounded_captures(self):
        payload = self.load('run-baremetal-sdk-original-init-092.py')['payload']
        self.assertIn('timeout_seconds=660', payload)
        self.assertIn('for target in (120,360,480,600,650,660)', payload)
        self.assertIn('if target==660:', payload)
        self.assertIn('disk_backed=True,test_only=True', payload)
        self.assertIn('original-graphics-provider-005', payload)
        self.assertIn('original-graphics-egl-009', payload)
        self.assertNotIn('original-init-qemu-091', payload)
        self.assertIn('readonly=on', payload)
        compile(payload, '<run092>', 'exec')

    def test_independent_hashes_and_extended_enforcing_gate(self):
        data = self.load('verify-original-graphics-boot-092.py')
        source = data['source']
        self.assertNotIn('original-init-qemu-091', source)
        self.assertIn('volume_checked', source)
        self.assertIn('independent_artifacts=json.loads(checked.stdout)', source.replace(' ', ''))
        self.assertIn('original_images_independent_hashes', source)
        tree = ast.parse(source)
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify_mode_samples')
        namespace = {'re': re}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<gate092>', 'exec'), namespace)
        raw = b''.join(f'GRAPHICS092_SELINUX sample={i} enforce=0\n'.encode() for i in range(72))
        self.assertEqual(namespace['verify_mode_samples'](raw, b'GRAPHICS092_'), 72)
        with self.assertRaises(AssertionError):
            namespace['verify_mode_samples'](raw.replace(b'enforce=0', b'enforce=1', 1), b'GRAPHICS092_')
        compile(source, '<verify092>', 'exec')


if __name__ == '__main__':
    unittest.main()
