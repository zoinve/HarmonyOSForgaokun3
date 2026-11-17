"""Validate observed-command grouping without invoking any target service."""
from pathlib import Path
import runpy
import unittest

parse = runpy.run_path(str(Path(__file__).with_name('analyze-oobe-single-launch-114.py')))['aa_commands']


def line(pid, index, value):
    return '11-15 23:53:46.138 ' + str(pid) + ' ' + str(pid) + ' I C01303/aa/AATool: [ability_command246]argv_[' + str(index) + ']: ' + value


class Commands(unittest.TestCase):
    def test_interleaved_processes(self):
        text = '\n'.join([line(1, 0, '/usr/bin/aa'), line(2, 0, '/system/bin/aa'),
                          line(1, 1, 'start'), line(2, 1, 'force-stop')])
        rows = parse(text)
        self.assertEqual(rows[0]['argv'], ['/usr/bin/aa', 'start'])
        self.assertEqual(rows[1]['argv'], ['/system/bin/aa', 'force-stop'])

    def test_missing_arguments_labelled(self):
        rows = parse(line(1, 0, '/usr/bin/aa') + '\n' + line(1, 2, '-b'))
        self.assertFalse(rows[0]['argv_records_contiguous'])

    def test_pid_reuse_new_command(self):
        rows = parse('\n'.join([line(1, 0, '/usr/bin/aa'), line(1, 1, 'start'),
                                line(1, 0, '/system/bin/aa'), line(1, 1, 'force-stop')]))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['argv'][1], 'start')

    def test_no_missing_prefix_invention(self):
        self.assertEqual(parse(line(1, 1, 'start')), [])


if __name__ == '__main__':
    unittest.main()
