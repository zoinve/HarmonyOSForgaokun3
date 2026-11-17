"""Narrow source guards before compiling target-only integration."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import unittest

BASE = Path(__file__).resolve().parent


class IntegrationTest(unittest.TestCase):
    def test_new_archive_contains_matching_modules_and_real_tools(self):
        work = Path('/home/zoinve/harmony-virgl-883')
        parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
        entries = {name:(mode,data) for name,mode,data in parser(gzip.decompress(
            (work / 'commercial61-native-502/minimal-overlay.img').read_bytes()))}
        modules = json.loads((BASE.parent / 'reports/compat-modules-500/result.json').read_text())
        for row in modules['matching_modules']:
            self.assertEqual(entries[row['path']][1],
                (work / 'compat-modules-500/root' / row['path']).read_bytes())
        self.assertNotIn('cpufreq471/icc-osm-l3.ko', entries)
        self.assertNotIn('native-target/share501/wlan.conf', entries)
        self.assertEqual(entries['native-target/share501'][0] & 0o777, 0o700)
        self.assertEqual(entries['native-target/share501/p2p.conf'][0] & 0o777, 0o400)
        self.assertIn('native-target/share494', entries)
        binary = entries['native-target/share501/wpa_supplicant'][1]
        expected = json.loads((BASE.parent / 'reports/share-supplicant-499/result.json').read_text())
        self.assertEqual(hashlib.sha256(binary).hexdigest(), expected['sha256'])

    def test_namespace_checks_and_real_backends_are_retained(self):
        source = runpy.run_path(str(BASE / 'share-network-helper-501.py'))['SOURCE']
        self.assertIn('setns(fds[i], kinds[i])', source)
        self.assertIn('!same(&after, &rootstat)', source)
        self.assertIn('share501_wlan()', source)
        self.assertIn('p2p_disabled=1', source)
        self.assertIn('"dev","wlan0","interface","add","p2p0","type","managed"', source)
        self.assertIn('"-ip2p0","-c/share501/p2p.conf"', source)
        self.assertIn('recv(fd,reply,sizeof(reply),0)', source)
        self.assertNotIn('system(', source)

    def test_magiclink_uses_normal_handshake_and_redacts_commands(self):
        patch = runpy.run_path(str(BASE / 'share-supplicant-patch-497.py'))
        self.assertIn('wpas_p2p_group_add_persistent', patch['WRAPPER'])
        self.assertIn('is_zero_ether_addr', patch['WRAPPER'])
        self.assertNotIn('P2P-GROUP-STARTED', patch['WRAPPER'])
        self.assertIn('[REMOVED]', (BASE / 'share-supplicant-patch-497.py').read_text())


if __name__ == '__main__':
    unittest.main()
