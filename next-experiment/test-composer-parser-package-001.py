"""Offline safety gate. Importing the builder must have no operational effects."""
from pathlib import Path
import importlib.util
import unittest

BASE = Path(__file__).resolve().parent


class PackageSafety(unittest.TestCase):
    def test_parser_builder_exists(self):
        self.assertTrue((BASE / 'build-composer-parser-001.py').is_file(),
                        'missing exclusive parser builder')

    def test_diskless_headless_command(self):
        path = BASE / 'build-composer-parser-001.py'
        if not path.exists():
            self.skipTest('builder not implemented')
        spec = importlib.util.spec_from_file_location('parser_builder', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cmd = mod.qemu_command('/kernel', '/initrd')
        self.assertIn('kvm', cmd)
        self.assertEqual(cmd[cmd.index('-display') + 1], 'none')
        self.assertEqual(cmd[cmd.index('-nic') + 1], 'none')
        self.assertIn('-nodefaults', cmd)
        for forbidden in ('-drive', '-blockdev', '-device', '-netdev', '-fsdev',
                          '-virtfs', '-hda', '-hdb', '-cdrom', '-bios'):
            self.assertNotIn(forbidden, cmd)
        self.assertNotIn('/dev/dri', ' '.join(cmd))

    def test_fresh_software_trial_preserves_failed_number(self):
        path = BASE / 'run-composer-parser-002.py'
        self.assertTrue(path.is_file())
        spec = importlib.util.spec_from_file_location('software_trial', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        source = mod.launcher_source()
        compile(source, 'software-trial-offline-check', 'exec')
        self.assertIn("command[command.index('-accel') + 1] = 'tcg,thread=multi'", source)
        self.assertIn("command[command.index('-cpu') + 1] = 'cortex-a72'", source)
        self.assertIn('reports/composer-parser-run-002', source)
        self.assertNotIn('reports/composer-parser-run-001', source)


if __name__ == '__main__':
    unittest.main()
