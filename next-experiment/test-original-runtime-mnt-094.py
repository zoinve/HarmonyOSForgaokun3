"""Offline gates only; never discover or execute operational experiments."""
from pathlib import Path
import ast
import runpy
import unittest

HERE = Path(__file__).parent


class RuntimeMountTests(unittest.TestCase):
    def test_original_early_mount_is_restored_after_guest_guards(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-094.py'
        self.assertTrue(path.exists(), 'missing guarded runtime-mount fixture')
        ns = runpy.run_path(str(path))
        s = ns['source']
        self.assertIn('mount("tmpfs", "/mnt", "tmpfs", MS_NOSUID, "mode=0755")', s)
        self.assertIn('mount(NULL, "/mnt", NULL, MS_SLAVE, NULL)', s)
        main = s[s.index('int main('):]
        self.assertLess(main.index('"dummy-virt"'), main.index('graphics_runtime_mnt_094();'))
        self.assertLess(main.index('graphics_runtime_mnt_094();'), main.index('execve(arguments[0]'))
        self.assertIn('MS_BIND | MS_REMOUNT | MS_RDONLY | MS_NODEV', s)
        self.assertIn('16777216', s)
        self.assertNotIn('setuid(', s)
        compile(ns['payload'], '094-prepare-offline', 'exec')

    def test_fresh_runner_and_full_independent_checks(self):
        for name in ('run-baremetal-sdk-original-init-094.py', 'verify-original-graphics-boot-094.py'):
            path = HERE / name
            self.assertTrue(path.exists(), f'missing {name}')
            ns = runpy.run_path(str(path))
            text = ns['payload'] if 'payload' in ns else ns['source']
            compile(text, name, 'exec')
            self.assertEqual(text.count('baremetal-sdk-original-init-qemu-093'), 0)
            if name.startswith('run-'):
                self.assertIn('original-graphics-provider-005', text)
                self.assertIn('original-graphics-egl-009', text)
                self.assertIn('(120,360,480,600,650,660)', text.replace(' ', ''))
                self.assertNotIn('ssh ', text)
            else:
                self.assertIn('original_images_independent_hashes', text)
                self.assertIn('independent_artifacts=json.loads(checked.stdout)', text)
                self.assertIn('physical_board_test=False', text)
                self.assertIn('observed_runtime_mounts', text)

    def test_failed_mount_observation_is_not_a_false_writable_result(self):
        ns = runpy.run_path(str(HERE / 'verify-original-graphics-boot-094.py'))
        rows = ns['parse_runtime_mounts'](
            b'GRAPHICS094_MOUNT_STATE sample=24 path=/mnt stat=-1 errno=5 flags=0\n'
            b'GRAPHICS094_MOUNT_STATE sample=24 path=/ stat=0 errno=0 flags=5\n')
        self.assertIsNone(rows[0]['flags'])
        self.assertEqual(rows[1]['flags'], 5)

    def test_generated_mount_reader_uses_existing_base_variable(self):
        ns = runpy.run_path(str(HERE / 'verify-original-graphics-boot-094.py'))
        statements = [n for n in ast.walk(ast.parse(ns['source']))
                      if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and
                          t.id == 'observed_runtime_mounts' for t in n.targets)]
        self.assertEqual(len(statements), 1)
        names = {n.id for n in ast.walk(statements[0].value) if isinstance(n, ast.Name)}
        self.assertNotIn('root', names)
        self.assertIn('BASE', names)


if __name__ == '__main__':
    unittest.main()
