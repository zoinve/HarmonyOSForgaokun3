from pathlib import Path
import runpy
import unittest

overlaps = runpy.run_path(str(Path(__file__).with_name('analyze-server-event-107.py')))['overlaps']


class SnapshotOverlapTests(unittest.TestCase):
    def test_missing_evidence_unknown(self):
        self.assertIsNone(overlaps('11-15', None, {}, {}))
        self.assertIsNone(overlaps('11-15', 10, None, {}))

    def test_different_day_unknown(self):
        start = dict(day='11-15', milliseconds=10)
        end = dict(day='11-15', milliseconds=20)
        self.assertIsNone(overlaps('01-01', 15, start, end))

    def test_before_after_not_overlap(self):
        start = dict(day='11-15', milliseconds=10)
        end = dict(day='11-15', milliseconds=20)
        self.assertFalse(overlaps('11-15', 9, start, end))
        self.assertFalse(overlaps('11-15', 21, start, end))

    def test_boundaries_inclusive(self):
        start = dict(day='11-15', milliseconds=10)
        end = dict(day='11-15', milliseconds=20)
        for value in (10, 15, 20):
            self.assertTrue(overlaps('11-15', value, start, end))


if __name__ == '__main__':
    unittest.main()
