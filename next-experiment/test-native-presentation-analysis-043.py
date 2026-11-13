"""Synthetic trace fixtures, not a hardware performance benchmark."""
from pathlib import Path
import runpy
import unittest

MODULE = Path(__file__).with_name('analyze-native-presentation-043.py')


def record(kind, ident, seq, time, origin='client', **extra):
    fields = dict(pid=123, uid=3036, kind=kind, origin=origin, id=ident, fb=8,
                  submit_us=time - 1000, callback_us=time, drm_seq=seq,
                  drm_sec=time // 1000000, drm_usec=time % 1000000,
                  timestamp_monotonic=1, matched=1, result=0, error=0)
    fields.update(extra)
    return ('NATIVE_PRESENT043 ' + ' '.join(f'{k}={v}' for k, v in fields.items()) + '\n').encode()


def pair(ident, seq, time, origin='client'):
    return record('submit', ident, 0, time, origin) + record('complete', ident, seq, time, origin)


class AnalysisTests(unittest.TestCase):
    def analyze(self, raw):
        self.assertTrue(MODULE.exists(), 'missing completion analyzer')
        return runpy.run_path(str(MODULE))['analyze'](raw)

    def test_cursor_updates_do_not_inflate_client_rate(self):
        raw = pair(1, 10, 1000000) + pair(2, 11, 1008333, 'cursor') + pair(3, 12, 1016666)
        result = self.analyze(raw + raw) # cumulative snapshots must deduplicate
        self.assertEqual(result['completed_client'], 2)
        self.assertEqual(result['completed_cursor'], 1)
        self.assertAlmostEqual(result['client_windows'][0]['observed_completion_hz'], 60, places=2)
        self.assertFalse(result['stable_120fps_verified'])
        self.assertFalse(result['unique_visual_content_verified'])

    def test_failed_or_unmatched_submissions_never_count(self):
        raw = record('submit', 1, 0, 1000000) + record('submit_failed', 1, 0, 1000000, result=-1)
        raw += record('complete', 1, 1, 1000000)
        raw += record('complete', 3, 3, 1020000, matched=0)
        raw += pair(4, 4, 1030000).replace(b'timestamp_monotonic=1', b'timestamp_monotonic=-1')
        raw += pair(5, 5, 1040000).replace(b'uid=3036', b'uid=0')
        result = self.analyze(raw)
        self.assertEqual(result['completed_client'], 0)
        self.assertEqual(result['client_windows'], [])

    def test_conflict_and_clock_regression_are_not_a_valid_window(self):
        raw = pair(1, 10, 1000000) + pair(2, 11, 999000)
        result = self.analyze(raw)
        self.assertEqual(result['client_windows'], [])
        self.assertTrue(result['ordering_anomalies'])
        raw = pair(1, 10, 1000000) + pair(1, 12, 1010000)
        self.assertEqual(self.analyze(raw)['completed_client'], 0)


if __name__ == '__main__':
    unittest.main()
