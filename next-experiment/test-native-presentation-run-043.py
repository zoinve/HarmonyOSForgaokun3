"""Offline scheduler, preflight and collector gates; no device operations."""
from pathlib import Path
import runpy
from types import SimpleNamespace
import json
import hashlib
import io
import subprocess
import tarfile
import unittest

HERE = Path(__file__).parent


class NativeRunTests(unittest.TestCase):
    def test_immediate_reconnect_never_accepts_old_boot(self):
        path = HERE / 'run-native-presentation-043.py'
        self.assertTrue(path.exists(), 'missing single-boot executor')
        ns = runpy.run_path(str(path))
        events = []
        stamp = [0.0]
        replies = iter([dict(boot_id='old', release='7.1.0-rc3-gaokun3+', cmdline='normal'),
                        dict(boot_id='new', release='7.1.0-rc3-gaokun3+', cmdline='normal')])
        def probe():
            events.append('probe')
            return SimpleNamespace(returncode=0, stdout=json.dumps(next(replies)), stderr='')
        def delay(seconds):
            events.append('delay')
            stamp[0] += seconds
        result = ns['observe_return']('old', probe=probe, clock=lambda: stamp[0], delay=delay, timeout=4)
        self.assertTrue(result['returned'])
        self.assertEqual(events, ['probe', 'delay', 'probe'])
        self.assertEqual(result['after_boot_id'], 'new')
        for name in ('PREPARE', 'REBOOT'):
            compile(ns[name], name, 'exec')
        self.assertIn('rows()==request[\'inventory\'][\'files\']', ns['PREPARE'])
        self.assertIn('triesLeft', ns['PREPARE'])
        self.assertIn("['bootctl','set-oneshot'", ns['PREPARE'])
        self.assertIn("'--no-block','reboot'", ns['REBOOT'])
        self.assertNotIn('sleep(20)', path.read_text())

    def test_collector_requires_real_lab_identity_and_read_only_mount(self):
        path = HERE / 'retrieve-native-presentation-043.py'
        self.assertTrue(path.exists(), 'missing bounded evidence collector')
        ns = runpy.run_path(str(path))
        text = ns['REMOTE']
        compile(text, '043-collector', 'exec')
        self.assertIn('00029cdd-1748-4d2f-b73b-8e8164922098', text)
        self.assertIn('24bd14b9-9d92-490a-ad15-a59c6b8e7cd9', text)
        self.assertIn('ro,noload,nodev,nosuid,noexec', text)
        self.assertIn('native-interactive-043-', text)
        self.assertNotIn('set-oneshot', text)
        self.assertNotIn('fsck', text)

    def test_collector_checks_real_members_and_rejects_path_traversal(self):
        ns = runpy.run_path(str(HERE / 'retrieve-native-presentation-043.py'))
        def blob(name):
            stream = io.BytesIO()
            with tarfile.open(fileobj=stream, mode='w') as archive:
                info = tarfile.TarInfo(name)
                info.size = 3
                archive.addfile(info, io.BytesIO(b'raw'))
            return stream.getvalue()
        manifest = dict(files={'phase-001.log':dict(bytes=3,sha256=hashlib.sha256(b'raw').hexdigest())})
        self.assertEqual(ns['validate_members'](blob('./phase-001.log'),manifest), {'phase-001.log':b'raw'})
        with self.assertRaises(AssertionError):
            ns['validate_members'](blob('../phase-001.log'),manifest)

    def test_reconnect_deadline_does_not_trigger_a_second_boot(self):
        ns = runpy.run_path(str(HERE / 'run-native-presentation-043.py'))
        clock = [0.0]
        calls = []
        def probe():
            calls.append('probe')
            clock[0] += 2
            raise subprocess.TimeoutExpired('ssh',2)
        result = ns['observe_return']('old',probe=probe,clock=lambda:clock[0],delay=lambda _:None,timeout=2)
        self.assertFalse(result['returned'])
        self.assertEqual(calls,['probe'])

    def test_independent_return_checks_preserve_fresh_entropy(self):
        path = HERE / 'verify-native-presentation-return-043.py'
        self.assertTrue(path.exists(), 'missing independent post-return verifier')
        ns = runpy.run_path(str(path))
        compile(ns['REMOTE'],'043-return-check','exec')
        self.assertIn('loader/random-seed',ns['REMOTE'])
        self.assertIn('set-property',ns['REMOTE'])
        self.assertNotIn("['bootctl','set-",ns['REMOTE'])
        self.assertIn('random_seed_not_restored',ns['REMOTE'])
        self.assertNotIn('.write_bytes(',ns['REMOTE'])

    def test_large_hilog_exception_is_exact_and_keeps_total_bound(self):
        path = HERE / 'retrieve-native-presentation-043-attempt-002.py'
        self.assertTrue(path.exists(), 'missing fresh collector for measured 81,132,855-byte HiLog')
        ns = runpy.run_path(str(path))
        self.assertEqual(ns['file_limit']('interactive-hilog030.log'), 128*1024*1024)
        self.assertEqual(ns['file_limit']('phase-069.log'), 64*1024*1024)
        self.assertEqual(ns['file_limit']('../interactive-hilog030.log'), 64*1024*1024)
        self.assertIn('512*1024*1024', ns['REMOTE'])
        self.assertIn('harmony-return-audit-043-attempt-002', ns['REMOTE'])
        compile(ns['REMOTE'], 'fresh-043-collector', 'exec')


if __name__ == '__main__':
    unittest.main()
