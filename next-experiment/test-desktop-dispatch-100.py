"""Focused regressions for read-only 100 event selection and clock guards."""
from pathlib import Path
import runpy
import unittest

AUDIT = runpy.run_path(str(Path(__file__).with_name('audit-desktop-dispatch-100.py')))


class TimelineTests(unittest.TestCase):
    def row(self, day='11-15', time='18:09:27.392', pid=4631, tid=4863, text='event'):
        return AUDIT['parse_line'](1, f'{day} {time} {pid} {tid} I tag: {text}'.encode())

    def test_timestamp_and_thread(self):
        row = self.row()
        self.assertEqual((row['pid'], row['tid']), (4631, 4863))
        self.assertEqual(row['milliseconds'], 65367392)

    def test_exact_elapsed(self):
        self.assertEqual(AUDIT['elapsed'](self.row(), self.row(time='18:09:43.139')), 15747)

    def test_clock_epoch_guard(self):
        with self.assertRaises(ValueError):
            AUDIT['elapsed'](self.row(day='01-01'), self.row())

    def test_backward_clock_guard(self):
        with self.assertRaises(ValueError):
            AUDIT['elapsed'](self.row(), self.row(time='18:09:20.000'))

    def test_ambiguous_event_refused(self):
        with self.assertRaises(ValueError):
            AUDIT['select_one']([self.row(), self.row()], b'event')

    def test_missing_event_refused(self):
        with self.assertRaises(ValueError):
            AUDIT['select_one']([self.row()], b'absent')

    def test_thread_filter(self):
        row = self.row(tid=4631)
        self.assertIs(AUDIT['select_one']([self.row(), row], b'event', tid=4631), row)

    def test_non_log_ignored(self):
        self.assertIsNone(AUDIT['parse_line'](1, b'continuation without timestamp'))


if __name__ == '__main__':
    unittest.main()
