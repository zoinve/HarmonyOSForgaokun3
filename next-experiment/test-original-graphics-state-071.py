"""Offline guards for read-only original-service state observation."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class StateObservation(unittest.TestCase):
    def test_passive_state_reads_do_not_modify_target(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-071.py'
        self.assertTrue(path.exists(), 'missing read-only state observer')
        source = runpy.run_path(str(path))['source']
        self.assertIn('GRAPHICS071_STATE', source)
        self.assertIn('pread(fd, &value, width', source)
        self.assertIn('O_RDONLY | O_CLOEXEC | O_NOFOLLOW', source)
        self.assertIn('0x83fab0', source)
        self.assertIn('0x14138', source)
        self.assertNotIn('PTRACE_', source)
        self.assertNotIn('pwrite(', source)
        self.assertNotIn('process_vm_writev', source)
        self.assertIn('private_hash_specific_state=1', source)

    def test_runner_preserves_isolation(self):
        path = HERE / 'run-baremetal-sdk-original-init-071.py'
        self.assertTrue(path.exists(), 'missing isolated state runner')
        payload = runpy.run_path(str(path))['payload']
        for name in ('original-init-qemu-071', 'original-init-071/result.json',
                     'virtio-mmio.force-legacy=false', 'readonly=on'):
            self.assertIn(name, payload)
        self.assertIn('original-graphics-provider-004', payload)
        self.assertIn('original-graphics-egl-009', payload)
        self.assertIn('360', payload)
        compile(payload, 'offline-state-071', 'exec')

    def test_failed_read_is_not_a_null_pointer_witness(self):
        path = HERE / 'verify-original-graphics-boot-071.py'
        self.assertTrue(path.exists(), 'missing independent state verifier')
        module = runpy.run_path(str(path))
        parse = module['parse_state_records']
        raw = (b'GRAPHICS071_STATE sample=17 pid=20 field=backend_device bytes=-1 errno=13 base=0x1000 value=0x0 private_hash_specific_state=1\n'
               b'GRAPHICS071_STATE sample=29 pid=20 field=backend_device bytes=8 errno=0 base=0x1000 value=0x0 private_hash_specific_state=1\n')
        rows = parse(raw)
        self.assertEqual(len(rows), 2)
        self.assertIsNone(rows[0]['value'])
        self.assertFalse(rows[0]['read_success'])
        self.assertTrue(rows[1]['read_success'])
        self.assertEqual(rows[1]['value'], 0)
        compile(module['source'], 'offline-state-verifier-071', 'exec')

    def test_original_entry_audit_is_read_only(self):
        path = HERE / 'audit-original-render-entry-001.py'
        self.assertTrue(path.exists(), 'missing original entry audit')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('/system/bin/render_service', payload)
        self.assertIn('original_system_unchanged=True', payload)
        self.assertIn('target_code_executed=False', payload)
        self.assertNotIn("'debugfs','-w'", payload)
        compile(payload, 'offline-original-entry-audit', 'exec')


if __name__ == '__main__':
    unittest.main()
