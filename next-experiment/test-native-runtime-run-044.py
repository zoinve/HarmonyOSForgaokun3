"""Offline gates: one fresh boot, bounded retrieval, unchanged telemetry format."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).parent


class RuntimeTests(unittest.TestCase):
    def load(self, name):
        path = HERE / name
        self.assertTrue(path.exists(), f'missing {name}')
        return runpy.run_path(str(path))

    def test_single_boot_keeps_immediate_reconnect_and_nonce(self):
        ns = self.load('run-native-presentation-044.py')
        compile(ns['source'], 'run044-offline', 'exec')
        self.assertIn('native-presentation-044-installation.json', ns['source'])
        self.assertIn("operation_nonce=str(uuid.uuid4())", ns['source'])
        self.assertNotIn('time.sleep(20)', ns['source'])
        events = []
        def probe():
            events.append('probe')
            raise TimeoutError('first probe reached without initial delay')
        with self.assertRaises(TimeoutError):
            ns['observe_return']('old', probe=probe, clock=lambda: 0,
                                 delay=lambda n: events.append('delay'))
        self.assertEqual(events, ['probe'])

    def test_collector_keeps_specific_log_exception_and_total_bound(self):
        ns = self.load('retrieve-native-presentation-044.py')
        compile(ns['source'], 'retrieve044-offline', 'exec')
        self.assertEqual(ns['file_limit']('interactive-hilog030.log'), 128*1024*1024)
        self.assertEqual(ns['file_limit']('phase-001.log'), 64*1024*1024)
        self.assertIn('512*1024*1024', ns['source'])
        self.assertIn('/mnt/harmony-return-audit-044', ns['source'])
        self.assertIn('native-interactive-044-', ns['source'])

    def test_verifier_requires_real_mount_marker_and_all_old_evidence(self):
        ns = self.load('verify-native-presentation-return-044.py')
        s = ns['source']
        compile(s, 'return044-offline', 'exec')
        for required in ('NATIVE_MNT044_READY', 'NATIVE_PRESENT043', 'prior043_raw_files_verified',
                         'original_sdk_images_verified=3', 'stable_120fps_verified=False',
                         'random_seed_not_restored=True', 'WouldChangeDisplay'):
            self.assertIn(required, s)
        self.assertIn("root = base/'reports/native-original-graphics-boot-044'", s)
        self.assertIn('native-original-graphics-044+0-1.conf', s)


if __name__ == '__main__':
    unittest.main()
