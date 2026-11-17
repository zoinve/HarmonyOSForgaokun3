"""Verify byte accounting retains original CLI CRLF and rejects corruption."""
from pathlib import Path
import runpy
import unittest

parse = runpy.run_path(str(Path(__file__).with_name('analyze-commercial-event-state-064.py')))['parse_streams']


def fixture(text, *, count=None, eof=1, errno=0):
    path = '/proc/298/root/data/commercial-event-state064.log'
    length = len(text.encode()) if count is None else count
    return (f'COMMERCIAL064_OUTER_STREAM_BEGIN path={path} limit=32768\n'
            f'{text}\nCOMMERCIAL064_OUTER_STREAM_END path={path} bytes={length} eof={eof} errno={errno}\n')


class Tests(unittest.TestCase):
    def test_original_crlf_preserved(self):
        text = 'COMMERCIAL064_ACL_BEGIN key=bootevent.account.ready\nParameter information:\r\n    value: true\r\n'
        result = parse(fixture(text))
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]['byte_count_matches'])
        self.assertEqual(result[0]['text'], text)

    def test_corruption_and_truncation_retained(self):
        records = parse(fixture('one\n', count=12) + fixture('two\n', eof=0) + fixture('', errno=2))
        self.assertEqual(len(records), 3)
        self.assertFalse(records[0]['byte_count_matches'])
        self.assertEqual(records[1]['eof'], 0)
        self.assertEqual(records[2]['errno'], 2)

    def test_nested_other_log_not_misidentified(self):
        other = fixture('account').replace('commercial-event-state064.log', 'commercial-account-order063.log')
        self.assertEqual(parse(other), [])


if __name__ == '__main__':
    unittest.main()
