"""Offline tests, with no operational experiment execution."""
from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class Safety(unittest.TestCase):
    def test_builder_present(self):
        self.assertTrue((BASE / 'build-composer-fdstream-001.py').is_file(), 'missing FD-stream builder')

    def test_command_is_opted_in_and_has_no_devices(self):
        p = BASE / 'build-composer-fdstream-001.py'
        if not p.exists():
            self.skipTest('not implemented')
        cmd = runpy.run_path(str(p), run_name='offline_test')['qemu_command']('/kernel', '/initrd')
        self.assertIn('harmony.smq.fdstream=1', cmd[cmd.index('-append') + 1])
        self.assertEqual(cmd[cmd.index('-accel') + 1], 'tcg,thread=multi')
        for flag in ('-device', '-drive', '-blockdev', '-fsdev', '-virtfs', '-netdev'):
            self.assertNotIn(flag, cmd)
        self.assertIn('-nodefaults', cmd)
        self.assertEqual(cmd[cmd.index('-nic') + 1], 'none')


if __name__ == '__main__':
    unittest.main()
