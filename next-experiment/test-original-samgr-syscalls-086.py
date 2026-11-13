"""Offline checks only: never execute a numbered guest launcher."""
from pathlib import Path
import runpy
import unittest

HERE = Path(__file__).resolve().parent


class AuditObservation(unittest.TestCase):
    def test_guest_rule_is_uid_scoped_and_never_changes_audit_receiver(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-086.py'
        self.assertTrue(path.exists(), 'missing UID-scoped guest audit fixture')
        source = runpy.run_path(str(path))['source']
        self.assertIn('AUDIT_ADD_RULE', source)
        self.assertIn('AUDIT_FILTER_EXIT', source)
        self.assertIn('AUDIT_UID', source)
        self.assertIn('5555', source)
        self.assertIn('SO_RCVTIMEO', source)
        self.assertNotRegex(source, r'\bAUDIT_SET\b')
        self.assertNotIn('AUDIT_SET_FEATURE', source)
        self.assertNotIn('AUDIT_DEL_RULE', source)
        self.assertLess(source.index('!strstr(buffer, "dummy-virt")'),
                        source.index('    graphics_audit_rule_086();'))
        self.assertLess(source.index('    graphics_audit_rule_086();'),
                        source.index('execve(arguments[0]'))

    def test_runner_only_enables_guest_logging_and_retains_readonly_images(self):
        path = HERE / 'run-baremetal-sdk-original-init-086.py'
        self.assertTrue(path.exists(), 'missing fresh audit observation runner')
        payload = runpy.run_path(str(path))['payload']
        compile(payload, 'offline-audit086-run', 'exec')
        self.assertIn('audit=1', payload)
        self.assertIn('format=raw,readonly=on', payload)
        self.assertIn('original-graphics-egl-009', payload)
        self.assertNotIn('ssh ', payload)

    def test_verifier_keeps_real_syscall_failures_and_rejects_other_uids(self):
        path = HERE / 'verify-original-graphics-boot-086.py'
        self.assertTrue(path.exists(), 'missing audit evidence verifier')
        module = runpy.run_path(str(path))
        rows = module['parse_audit_syscalls'](
            b'type=1300 audit(8.12:42): arch=c00000b7 syscall=56 success=no exit=-13 pid=133 uid=5555 euid=5555\n'
            b'type=1302 audit(8.12:42): item=0 name="/usr/system/profile"\n'
            b'type=1300 audit(8.13:43): arch=c00000b7 syscall=56 success=yes exit=7 pid=1 uid=0 euid=5555\n')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['exit'], -13)
        self.assertEqual(rows[0]['pid'], 133)
        self.assertIn('/usr/system/profile', rows[0]['related_records'][0])
        compile(module['source'], 'offline-audit086-verifier', 'exec')

    def test_verifier_rejects_interleaved_audit_headers(self):
        module = runpy.run_path(str(HERE / 'verify-original-graphics-boot-086.py'))
        raw = (b'type=1300 audit(8.12:42): arch=c00000b7 syscall=56 exit=-2 pid=133 uid=5555 '
               b'type=1300 audit(8.13:43): arch=c00000b7 syscall=56 exit=7 pid=1 uid=0\n')
        self.assertEqual(module['parse_audit_syscalls'](raw), [])
        # Also reject the inverse: another process's event must not acquire SAMGR's identity.
        raw = (b'type=1300 audit(8.12:42): arch=c00000b7 syscall=56 exit=-2 pid=1 uid=0 '
               b'type=1300 audit(8.13:43): arch=c00000b7 syscall=56 exit=7 pid=133 uid=5555\n')
        self.assertEqual(module['parse_audit_syscalls'](raw), [])


if __name__ == '__main__':
    unittest.main()
