"""Verify current and compressed historical evidence against canonical hashes."""
from pathlib import Path
import hashlib
import json
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
open_log = runpy.run_path(str(Path(__file__).with_name('compress-historical-logs-226.py')))['open_log']


class CleanedEvidenceTests(unittest.TestCase):
    def test_current_and_historical_members(self):
        for run in ['commercial61-native-001', 'commercial61-native-173', 'commercial61-native-206']:
            folder = ROOT / 'reports' / run / 'runtime-evidence'
            manifest = json.loads((folder / 'retrieval-manifest.json').read_text())
            for name in ['phase-001.log', 'interactive-hilog030.log']:
                with self.subTest(run=run, name=name):
                    expected = manifest['files'][name]
                    with open_log(folder / 'raw' / name) as stream:
                        actual = hashlib.file_digest(stream, 'sha256').hexdigest()
                    self.assertEqual(actual, expected['sha256'])

    def test_current_logs_remain_plaintext(self):
        for run in ['commercial61-native-173', 'commercial61-native-206']:
            path = ROOT / 'reports' / run / 'runtime-evidence/raw/interactive-hilog030.log'
            self.assertTrue(path.is_file())
            self.assertFalse(path.with_name(path.name + '.gz').exists())


if __name__ == '__main__':
    unittest.main()
