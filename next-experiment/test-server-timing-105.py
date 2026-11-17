from pathlib import Path
import runpy
import unittest

QUERY = runpy.run_path(str(Path(__file__).with_name('analyze-server-timing-105.py')))['query_events']
START = b'device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start'
END = b'device_picker_client.cpp:396]GetTrustedDeviceListWithAbilityFilter# end'
REQUEST = b'ReadAbilityFilterList# abilityFilterList length:3'
STAGE = b'GetTrustedDeviceListWithAbilityFilter# event = SERVICE_COLLABORATION_EVENT; stage = 1; res = 1; err = 0'
REPLY = b'CheckDeviceAndReplySync# CheckDeviceAndReplySync deviceNum:0'


def rows(values):
    return [dict(line=i, milliseconds=ms, pid=pid, tid=tid, body=body)
            for i, (ms, pid, tid, body) in enumerate(values, 1)]


class TimingTests(unittest.TestCase):
    def test_complete_query(self):
        data = rows([(100, 40, 40, START), (101, 90, 91, REQUEST),
                     (500, 90, 91, STAGE), (1000, 90, 91, REPLY), (1001, 40, 40, END)])
        result = QUERY(data, 40, 90)
        self.assertEqual(result['server_read_request']['tid'], 91)
        self.assertEqual(result['client_end']['milliseconds'], 1001)

    def test_later_server_query_reply_not_attributed_to_incomplete_first(self):
        data = rows([(100, 40, 40, START), (101, 90, 91, REQUEST),
                     (150, 90, 91, REQUEST), (151, 90, 91, STAGE), (152, 90, 91, REPLY)])
        result = QUERY(data, 40, 90)
        self.assertIsNone(result['server_stage1'])
        self.assertIsNone(result['server_reply'])
        self.assertIsNone(result['client_end'])

    def test_later_same_client_start_bounds_incomplete_first(self):
        data = rows([(100, 40, 40, START), (101, 90, 91, REQUEST),
                     (150, 40, 40, START), (151, 90, 91, STAGE),
                     (152, 90, 91, REPLY), (153, 40, 40, END)])
        result = QUERY(data, 40, 90)
        self.assertIsNone(result['client_end'])
        self.assertIsNone(result['server_reply'])

    def test_wrong_process_and_thread_are_excluded(self):
        data = rows([(100, 40, 40, START), (101, 90, 91, REQUEST),
                     (102, 90, 92, REPLY), (103, 99, 91, REPLY), (104, 41, 41, END)])
        result = QUERY(data, 40, 90)
        self.assertIsNone(result['server_reply'])
        self.assertIsNone(result['client_end'])


if __name__ == '__main__':
    unittest.main()
