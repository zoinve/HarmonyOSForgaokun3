"""Test query timing without treating an unfinished or cross-clock call as fast."""
from pathlib import Path
import runpy
import unittest

parse = runpy.run_path(str(Path(__file__).with_name('analyze-oobe-checkpoint-116.py')))['query_pairs']


def line(pid, stamp, action, day='11-16'):
    return (day + ' ' + stamp + '  ' + str(pid) + '  ' + str(pid) +
            ' I C04613/com.ohos.sceneboard/CFWKProxy: [device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# ' + action).encode()


class Queries(unittest.TestCase):
    def test_seven_milliseconds(self):
        rows = parse([line(1, '01:44:19.246', 'start'), line(1, '01:44:19.253', 'end')])
        self.assertEqual(rows[0]['duration_ms'], 7)

    def test_replacement_pid_does_not_finish_old_call(self):
        rows = parse([line(1, '01:44:01.094', 'start'), line(2, '01:44:19.246', 'start'),
                      line(2, '01:44:19.253', 'end')])
        self.assertIsNone(rows[0]['duration_ms'])
        self.assertEqual(rows[1]['duration_ms'], 7)

    def test_cross_day_not_subtracted(self):
        rows = parse([line(1, '08:00:30.000', 'start', '01-01'), line(1, '01:44:19.253', 'end')])
        self.assertIsNone(rows[0]['duration_ms'])

    def test_backward_clock_not_subtracted(self):
        rows = parse([line(1, '01:44:19.253', 'start'), line(1, '01:44:19.246', 'end')])
        self.assertIsNone(rows[0]['duration_ms'])

    def test_end_without_start_not_invented(self):
        self.assertEqual(parse([line(1, '01:44:19.253', 'end')]), [])


if __name__ == '__main__':
    unittest.main()
