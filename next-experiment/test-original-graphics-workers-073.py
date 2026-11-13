"""Bounded passive worker coverage, not a claim about unsampled threads."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class WorkerObservation(unittest.TestCase):
    def test_worker_sampling_is_bounded_and_read_only(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-073.py'
        self.assertTrue(path.exists(), 'missing wider worker observer')
        source = runpy.run_path(str(path))['source']
        self.assertIn('tid_count < 128', source)
        self.assertIn('"comm", "wchan", "syscall"', source)
        self.assertIn('k < sizeof(kinds) / sizeof(kinds[0])', source)
        self.assertNotIn('PTRACE_', source)
        self.assertNotIn('pwrite(', source)
        self.assertIn('O_RDONLY | O_CLOEXEC | O_NOFOLLOW', source)

    def test_runner_and_verifier_keep_original_graph(self):
        runner = HERE / 'run-baremetal-sdk-original-init-073.py'
        verifier = HERE / 'verify-original-graphics-boot-073.py'
        self.assertTrue(runner.exists(), 'missing isolated worker runner')
        self.assertTrue(verifier.exists(), 'missing independent worker verifier')
        payload = runpy.run_path(str(runner))['payload']
        for text in ('original-init-qemu-073', 'original-init-073/result.json',
                     'original-graphics-egl-009', 'original-graphics-provider-004',
                     'readonly=on', 'virtio-mmio.force-legacy=false'):
            self.assertIn(text, payload)
        module = runpy.run_path(str(verifier))
        self.assertIn('(comm|wchan|syscall)', module['source'])
        raw = b'GRAPHICS073_STATE sample=17 pid=42 field=composer_remote bytes=-1 errno=13 base=0x1000 value=0x0 private_hash_specific_state=1\n'
        self.assertIsNone(module['parse_state_records'](raw)[0]['value'])
        compile(module['source'], 'offline-worker-verifier-073', 'exec')


if __name__ == '__main__':
    unittest.main()
