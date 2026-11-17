"""Focused parser tests; empty cards and truncated reads cannot prove playback."""
from pathlib import Path
import runpy
import unittest

summarize = runpy.run_path(str(Path(__file__).with_name('analyze-native-media-138.py')))['summarize']


class MediaAnalysis(unittest.TestCase):
    def test_no_cards(self):
        text = ('MEDIA136_FILE_BEGIN stage=services_sample136 path=/proc/asound/cards limit=8192\n'
                '--- no soundcards ---\n\nMEDIA136_FILE_END stage=services_sample136 '
                'path=/proc/asound/cards bytes=22 eof=1 errno=0\n')
        result = summarize(text)
        self.assertEqual(len(result['file_samples']), 1)
        self.assertFalse(result['alsa_card_observed'])
        self.assertFalse(result['audio_playback_verified'])

    def test_enumeration_not_acceptance(self):
        text = ('MEDIA136_FILE_BEGIN stage=services_sample136 path=/proc/asound/cards limit=8192\n'
                ' 0 [SC8280XPHUAWEIG]: sc8280xp\n\nMEDIA136_FILE_END stage=services_sample136 '
                'path=/proc/asound/cards bytes=36 eof=1 errno=0\n'
                'MEDIA136_CLASS_ENTRY stage=services_sample136 path=/sys/class/bluetooth/hci0 controller_ready_not_inferred=1\n')
        result = summarize(text)
        self.assertTrue(result['alsa_card_observed'])
        self.assertTrue(result['hci_class_observed'])
        self.assertFalse(result['native_audio_hdi_verified'])
        self.assertFalse(result['bluetooth_pairing_verified'])

    def test_incomplete_record_not_parsed(self):
        result = summarize('MEDIA136_FILE_BEGIN stage=x path=/proc/asound/cards limit=8192\n 0 [card]')
        self.assertFalse(result['alsa_card_observed'])


if __name__ == '__main__':
    unittest.main()
