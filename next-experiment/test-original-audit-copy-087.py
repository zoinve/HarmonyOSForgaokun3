"""Offline safety checks only; never launch an operational experiment."""
from pathlib import Path
import re
import runpy
import unittest

HERE = Path(__file__).parent


class AuditCopyTests(unittest.TestCase):
    def test_guest_copy_is_multicast_only_and_bounded(self):
        path = HERE / 'prepare-baremetal-sdk-original-init-087.py'
        self.assertTrue(path.exists(), 'missing fresh 087 fixture')
        module = runpy.run_path(str(path))
        source = module['source']
        helper = module['helper']
        self.assertIn('AUDIT_NLGRP_READLOG', helper)
        self.assertIn('60', helper)
        self.assertIn('64U * 1024U * 1024U', helper)
        self.assertIn('O_EXCL | O_NOFOLLOW', helper)
        self.assertIn('MSG_TRUNC', helper)
        self.assertIn('sender.nl_pid != 0', helper)
        self.assertNotRegex(helper, r'\b(AUDIT_SET|AUDIT_DEL_RULE|sendto|sendmsg)\b')
        self.assertLess(source.index('!strstr(buffer, "dummy-virt")'),
                        source.index('    graphics_audit_copy_087();'))
        self.assertLess(source.index('    graphics_audit_copy_087();'),
                        source.index('    graphics_audit_rule_086();'))
        compile(module['payload'], str(path), 'exec')

    def test_new_run_keeps_original_graph_and_images(self):
        path = HERE / 'run-baremetal-sdk-original-init-087.py'
        self.assertTrue(path.exists(), 'missing fresh 087 runner')
        payload = runpy.run_path(str(path))['payload']
        self.assertIn('original-init-qemu-087', payload)
        self.assertIn('original-init-087/result.json', payload)
        self.assertIn('audit=1', payload)
        self.assertIn('readonly=on', payload)
        self.assertIn('original-graphics-provider-005', payload)
        self.assertIn('original-graphics-egl-009', payload)
        self.assertNotRegex(payload, r'\bssh\b')
        compile(payload, str(path), 'exec')

    def test_recovery_and_verifier_keep_raw_return_codes(self):
        path = HERE / 'verify-original-graphics-boot-087.py'
        self.assertTrue(path.exists(), 'missing fresh 087 verifier')
        recovery = HERE / 'recover-original-audit-copy-087.py'
        self.assertTrue(recovery.exists(), 'missing disposable-copy recovery')
        module = runpy.run_path(str(path))
        raw = (b'type=1300 audit(1.0:8): arch=c00000b7 syscall=56 exit=-13 pid=131 uid=5555 success=no\n'
               b'type=1302 audit(1.0:8): name=2F7573722F73797374656D2F70726F66696C65\n'
               b'type=1300 audit(1.0:9): arch=c00000b7 syscall=56 exit=7 pid=9 uid=0 success=yes\n')
        rows = module['parse_audit_copy'](raw)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['exit'], -13)
        self.assertEqual(rows[0]['paths'], ['/usr/system/profile'])
        self.assertIn('original_scratch_unchanged', module['source'])
        self.assertIn('physical_board_test=False', module['source'])
        compile(module['source'], str(path), 'exec')
        payload = runpy.run_path(str(recovery))['payload']
        self.assertIn("original.open('rb')", payload)
        self.assertIn("recovered.open('xb')", payload)
        self.assertIn("['e2fsck','-f','-p',str(recovered)]", payload)
        compile(payload, str(recovery), 'exec')


if __name__ == '__main__':
    unittest.main()
