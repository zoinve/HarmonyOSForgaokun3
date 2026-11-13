"""Offline guards for all-process, read-only original graph sampling."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class RoleObservation(unittest.TestCase):
    def test_samples_each_original_render_process_without_attaching(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-072.py'
        self.assertTrue(path.exists(), 'missing all-process observer')
        source = runpy.run_path(str(path))['source']
        self.assertIn('graphics_role_read_072(sample, pid)', source)
        self.assertIn('GRAPHICS072_ROLE', source)
        self.assertIn('"wchan", "syscall"', source)
        self.assertIn('tid_count < 16', source)
        self.assertNotIn('PTRACE_', source)
        self.assertNotIn('pwrite(', source)
        self.assertIn('O_RDONLY | O_CLOEXEC | O_NOFOLLOW', source)
        self.assertIn('sample == 17 || sample == 29 || sample == 41', source)

    def test_runner_keeps_same_graph_and_isolation(self):
        path = HERE / 'run-baremetal-sdk-original-init-072.py'
        self.assertTrue(path.exists(), 'missing isolated role runner')
        payload = runpy.run_path(str(path))['payload']
        for text in ('original-init-qemu-072', 'original-init-072/result.json',
                     'original-graphics-egl-009', 'original-graphics-provider-004',
                     'readonly=on', 'virtio-mmio.force-legacy=false'):
            self.assertIn(text, payload)
        compile(payload, 'offline-role-runner-072', 'exec')

    def test_verifier_keeps_unknown_reads_and_actual_parent_ids(self):
        path = HERE / 'verify-original-graphics-boot-072.py'
        self.assertTrue(path.exists(), 'missing independent all-process verifier')
        module = runpy.run_path(str(path))
        raw = b'GRAPHICS072_STATE sample=17 pid=42 field=composer_remote bytes=-1 errno=13 base=0x1000 value=0x0 private_hash_specific_state=1\n'
        self.assertIsNone(module['parse_state_records'](raw)[0]['value'])
        source = module['source']
        self.assertIn('observed_original_process_roles', source)
        self.assertIn('observed_original_thread_state', source)
        self.assertIn('actual_original_rs_thread_state', source)
        compile(source, 'offline-role-verifier-072', 'exec')


if __name__ == '__main__':
    unittest.main()
