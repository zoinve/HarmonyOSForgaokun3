"""Offline gates only: never execute an operational launcher here."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class BinderObservationTests(unittest.TestCase):
    def test_corrupted_uid_record_is_unknown_not_assumed_or_accepted(self):
        path = HERE / 'original-graphics-identity-records-001.py'
        self.assertTrue(path.exists(), 'missing explicit incomplete identity audit')
        audit = runpy.run_path(str(path))['audit_identities']
        raw = (b'GRAPHICS070_IDENTITY pid=965 Uid:[ 82.9] kernel message\n'
               b'\t3036\t3036\t3036\t3036\n'
               b'GRAPHICS070_DOMAIN pid=965 value=u:r:composer_host:s0\n'
               b'GRAPHICS070_IDENTITY pid=1154 Uid:\t3036\t3036\t3036\t3036\n'
               b'GRAPHICS070_DOMAIN pid=1154 value=u:r:composer_host:s0\n')
        role = audit(raw, b'GRAPHICS070_', [965, 1154], 3036, 'composer_host')
        self.assertEqual(role['pids'], [1154])
        self.assertEqual(role['incomplete_identity_pids'], [965])
        with self.assertRaises(AssertionError):
            audit(raw.replace(b'Uid:\t3036', b'Uid:\t0'), b'GRAPHICS070_', [1154], 3036, 'composer_host')

    def test_passive_guest_diagnostics_keep_original_graph(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-070.py'
        self.assertTrue(path.exists(), 'missing passive Binder observation fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('GRAPHICS070_BINDER_READ', source)
        self.assertIn('MS_NOSUID | MS_NODEV | MS_NOEXEC', source)
        self.assertIn('O_RDONLY | O_CLOEXEC | O_NOFOLLOW', source)
        self.assertIn('failed_transaction_log', source)
        self.assertIn('composer_pid', source)
        self.assertNotIn('setuid(', source)
        self.assertNotIn('setcon(', source)
        self.assertNotIn('binder_debug_mask', source)
        self.assertIn('guest_permissive_config_047();', source)

    def test_launcher_changes_only_observer_not_graphics_libraries(self):
        path = HERE / 'run-baremetal-sdk-original-init-070.py'
        self.assertTrue(path.exists(), 'missing isolated Binder diagnostic launcher')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('original-init-070/result.json', payload)
        self.assertIn('original-graphics-provider-004/result.json', payload)
        self.assertIn('original-graphics-egl-009/result.json', payload)
        self.assertIn('virtio-mmio.force-legacy=false', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertNotIn('setenforce', payload)

    def test_verifier_records_failures_without_fabricating_connectivity(self):
        path = HERE / 'verify-original-graphics-boot-070.py'
        self.assertTrue(path.exists(), 'missing Binder diagnostic verifier')
        source = runpy.run_path(str(path))['source']
        compile(source, 'offline-binder-verifier', 'exec')
        self.assertIn('observed_binder_reads', source)
        self.assertIn('observed_binder_mounts', source)
        self.assertIn('readiness_verified=False', source)
        self.assertIn('original-graphics-provider-004', source)


if __name__ == '__main__':
    unittest.main()
