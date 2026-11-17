"""Keep volume diagnostics separate from arbitrary key/identity logging."""
from pathlib import Path
import io
import json
import runpy
import unittest

INSPECT = runpy.run_path(str(Path(__file__).with_name('analyze-volume-keys-486.py')))['inspect']


class VolumeTest(unittest.TestCase):
    def test_only_allowlisted_payload_is_exported(self):
        text = '''(SetVolume:42) volume=7 result=0 address=AA:BB:CC:DD:EE:FF name=PRIVATE_DEVICE
(SendPassThrough:43) volume_down action=0 keyCode=17
(OnKeyEvent:44) keyCode=30 text=PRIVATE_TYPED
(GetVolume:45) passkey=123456 result=0
'''
        result = INSPECT(io.BytesIO(text.encode()))
        serialized = json.dumps(result)
        for secret in ('AA:BB', 'PRIVATE_DEVICE', 'PRIVATE_TYPED', '123456', 'keycode'):
            self.assertNotIn(secret, serialized)
        self.assertEqual(len(result['records']), 2)
        self.assertTrue(result['records'][1]['volume_down_word_seen'])
        self.assertFalse(result['volume_down_repaired_or_ui_accepted'])


if __name__ == '__main__':
    unittest.main()
