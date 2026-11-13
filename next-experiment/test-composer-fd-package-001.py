"""Offline gates; never launch historical operational experiments."""
from pathlib import Path
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class Safety(unittest.TestCase):
    def test_fd_package_present(self):
        self.assertTrue((BASE / 'build-composer-fd-001.py').is_file(), 'missing FD package builder')

    def test_no_device_software_command(self):
        path = BASE / 'build-composer-fd-001.py'
        if not path.exists():
            self.skipTest('not implemented')
        cmd = runpy.run_path(str(path), run_name='offline_test')['qemu_command']('/kernel', '/initrd')
        self.assertEqual(cmd[cmd.index('-accel') + 1], 'tcg,thread=multi')
        self.assertEqual(cmd[cmd.index('-cpu') + 1], 'cortex-a72')
        for flag in ('-drive', '-device', '-blockdev', '-fsdev', '-virtfs', '-netdev'):
            self.assertNotIn(flag, cmd)
        self.assertIn('-nodefaults', cmd)
        self.assertEqual(cmd[cmd.index('-nic') + 1], 'none')


if __name__ == '__main__':
    unittest.main()
