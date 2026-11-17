from pathlib import Path
import json
import runpy
import unittest

scan = runpy.run_path(str(Path(__file__).with_name('inspect-share-data-512.py')))['scan']


class PrivacyTest(unittest.TestCase):
    def test_only_known_labels_and_numeric_results_leave_the_reader(self):
        result = scan([b'P2P-GROUP-STARTED secret-ssid psk=private-key\n',
                       b'12.345 configure-go-ip a=2412 b=0 result=0\n',
                       b'nl80211: Failed to join private-peer\n',
                       b'12.345 unknown-peer-name a=1 b=2 result=0\n'])
        self.assertEqual(result['events']['group_started'],1)
        self.assertEqual(result['group_results'],[dict(kind='configure-go-ip',result=0,count=1)])
        for secret in ['secret-ssid','private-key','private-peer','unknown-peer-name']:
            self.assertNotIn(secret,json.dumps(result))
        self.assertFalse(result['file_transfer_verified'])


if __name__ == '__main__':
    unittest.main()
