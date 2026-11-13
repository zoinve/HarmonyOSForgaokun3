"""Offline safety gates; never execute a numbered operational experiment."""
from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class Safety(unittest.TestCase):
    def test_verifier_accounts_for_legacy_marker_mismatch(self):
        p = BASE / 'verify-composer-queue-001.py'
        if not p.exists():
            self.skipTest('not implemented')
        source = runpy.run_path(str(p), run_name='offline_test')['launcher_source']()
        self.assertIn('launcher_marker_mismatch=True', source)
        self.assertIn('composer_request_not_tested=1 desktop_not_tested=1', source)

    def test_builder_present(self):
        self.assertTrue((BASE / 'build-composer-queue-001.py').is_file(), 'missing queue builder')

    def test_command_is_opted_in_and_isolated(self):
        p = BASE / 'build-composer-queue-001.py'
        if not p.exists():
            self.skipTest('not implemented')
        cmd = runpy.run_path(str(p), run_name='offline_test')['qemu_command']('/kernel', '/initrd')
        self.assertIn('harmony.smq.queue=1', cmd[cmd.index('-append') + 1])
        self.assertEqual(cmd[cmd.index('-accel') + 1], 'tcg,thread=multi')
        self.assertEqual(cmd[cmd.index('-display') + 1], 'none')
        self.assertEqual(cmd[cmd.index('-nic') + 1], 'none')
        self.assertIn('-nodefaults', cmd)
        for flag in ('-device', '-drive', '-blockdev', '-fsdev', '-virtfs', '-netdev'):
            self.assertNotIn(flag, cmd)


if __name__ == '__main__':
    unittest.main()
