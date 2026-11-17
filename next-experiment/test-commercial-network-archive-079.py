from pathlib import Path
import runpy
import stat
import unittest

parse = runpy.run_path(str(Path(__file__).with_name('audit-commercial-network-inputs-079.py')))['members']


def entry(name, data=b'', mode=stat.S_IFREG | 0o644):
    encoded = name.encode() + b'\0'
    values = [1, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(encoded), 0]
    header = b'070701' + b''.join(f'{value:08x}'.encode() for value in values)
    record = header + encoded
    record += b'\0' * (-len(record) % 4)
    record += data
    return record + b'\0' * (-len(record) % 4)


class ArchiveTests(unittest.TestCase):
    def test_complete_file(self):
        result = list(parse(entry('./lib/firmware/test', b'abc') + entry('TRAILER!!!')))
        self.assertEqual(result[0][0], 'lib/firmware/test')
        self.assertEqual(result[0][2], b'abc')

    def test_preserve_symlink(self):
        result = list(parse(entry('hw2.1', b'hw2.0', stat.S_IFLNK | 0o777) + entry('TRAILER!!!')))
        self.assertTrue(stat.S_ISLNK(result[0][1]))
        self.assertEqual(result[0][2], b'hw2.0')

    def test_reject_truncated_header(self):
        with self.assertRaises(AssertionError):
            list(parse(b'070701'))

    def test_reject_missing_trailer(self):
        with self.assertRaises(AssertionError):
            list(parse(entry('test', b'abc')))

    def test_reject_path_escape(self):
        for name in ('../outside', '/absolute', 'lib/../../outside'):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                list(parse(entry(name) + entry('TRAILER!!!')))

    def test_reject_nonzero_suffix(self):
        with self.assertRaises(AssertionError):
            list(parse(entry('TRAILER!!!') + b'nonzero'))


if __name__ == '__main__':
    unittest.main()
