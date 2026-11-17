"""Exercise the exact observation shell against temporary synthetic sysfs."""
from pathlib import Path
import ast
import re
import runpy
import subprocess
import tempfile
import unittest

module = runpy.run_path(str(Path(__file__).with_name('build-commercial-native-080.py')))
block = module['NETWORK'].split('char *net080[] = ', 1)[1].split('NULL};', 1)[0]
strings = [ast.literal_eval(s) for s in re.findall(r'"(?:\\.|[^"\\])*"', block)]
assert strings[:3] == ['/bin/busybox', 'sh', '-c']
SCRIPT = ''.join(strings[3:])


class ObservationTests(unittest.TestCase):
    def run_fixture(self, physical=False, interface_only=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            net = root / 'net'
            net.mkdir()
            (net / 'lo').mkdir()
            if physical or interface_only:
                (net / 'wlan0').mkdir()
            if physical:
                (root / 'phy0').mkdir()
                (net / 'wlan0/phy80211').symlink_to(root / 'phy0')
            script = SCRIPT.replace('/sys/class/net', str(net)).replace('/bin/busybox', '/bin/true')
            return subprocess.run(['/bin/sh', '-c', script], text=True, capture_output=True, timeout=5)

    def test_absent_phy_exhausts_bound_without_success(self):
        result = self.run_fixture()
        self.assertEqual(result.returncode, 124)
        self.assertIn('NETWORK080_POLLS=40', result.stdout)
        self.assertNotIn('NETWORK080_PHY_OBSERVED=', result.stdout)

    def test_interface_name_alone_is_not_phy(self):
        result = self.run_fixture(interface_only=True)
        self.assertEqual(result.returncode, 124)
        self.assertNotIn('NETWORK080_PHY_OBSERVED=', result.stdout)

    def test_actual_phy_link_stops_poll_without_connectivity_claim(self):
        result = self.run_fixture(physical=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('NETWORK080_POLLS=0', result.stdout)
        self.assertIn('NETWORK080_PHY_OBSERVED=', result.stdout)
        self.assertIn('END_NOT_CONNECTIVITY', result.stdout)


if __name__ == '__main__':
    unittest.main()
