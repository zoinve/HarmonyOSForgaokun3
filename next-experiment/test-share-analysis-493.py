"""The diagnostic must never copy messages or peer identities."""
from pathlib import Path
import json
import runpy
import unittest

inspect = runpy.run_path(str(Path(__file__).with_name('analyze-share-492.py')))['inspect']


class PrivacyTest(unittest.TestCase):
    def test_counts_without_peer_data(self):
        result = inspect([
            b'(GetWifiP2pGroupInfo:12) p2p failed peer=private-peer',
            b'(Connect:13) softbus credential=private-key failed',
            b'(Ignore:14) unrelated failed',
            b'(Scan:15) p2p ready name=private-name',
        ])
        self.assertEqual(result['function_counts'], {'GetWifiP2pGroupInfo': 1, 'Scan': 1})
        self.assertEqual(result['failure_word_counts'], {'GetWifiP2pGroupInfo': 1})
        self.assertNotIn('private-', json.dumps(result))
        self.assertFalse(result['huawei_share_transfer_verified'])


if __name__ == '__main__':
    unittest.main()
