from pathlib import Path
import runpy
import unittest

inspect = runpy.run_path(str(Path(__file__).with_name('trace-stream-admission-085.py')))['inspect_streams']


def stream(sample, body, count=None, limit=100):
    count = len(body) if count is None else count
    return (f'COMMERCIAL043_STREAM_BEGIN sample={sample} pid=0 path=/data/native-perf-023.trace limit={limit}\n'.encode() +
            body + f'\nCOMMERCIAL043_STREAM_END sample={sample} pid=0 path=/data/native-perf-023.trace bytes={count} eof=1 errno=0\n'.encode())


class StreamTests(unittest.TestCase):
    def test_complete_bytes_admitted(self):
        result = inspect(stream(1, b'abc\n'))
        self.assertEqual(result['valid'][0]['body'], b'abc\n')
        self.assertFalse(result['rejected'])

    def test_interleaved_extra_bytes_not_admitted(self):
        result = inspect(stream(1, b'abcEXTRA', count=3))
        self.assertFalse(result['valid'])
        self.assertEqual(result['rejected'][0]['actual_body_bytes'], 8)

    def test_overlimit_refused(self):
        self.assertFalse(inspect(stream(1, b'abcd', limit=3))['valid'])

    def test_independent_good_stream_survives_corrupt_one(self):
        result = inspect(stream(1, b'bad', count=1) + stream(2, b'good'))
        self.assertEqual([row['sample'] for row in result['valid']], [2])
        self.assertEqual([row['sample'] for row in result['rejected']], [1])

    def test_unterminated_stream_not_admitted(self):
        self.assertFalse(inspect(stream(1, b'abc').split(b'COMMERCIAL043_STREAM_END')[0])['valid'])


if __name__ == '__main__':
    unittest.main()
