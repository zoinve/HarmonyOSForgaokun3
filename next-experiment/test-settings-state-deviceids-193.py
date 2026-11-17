from pathlib import Path
import runpy
import unittest

API = runpy.run_path(str(Path(__file__).with_name('audit-settings-state-deviceids-193.py')))


class Tests(unittest.TestCase):
    def test_empty_zero_and_unknown_kept_distinct(self):
        self.assertEqual(API['classify']([None, '', b'', 0, '0', b'0', 'old-device']),
                         dict(null=1, empty=2, zero=3, nonempty_nonzero=1))

    def test_other_constants_not_assumed_local(self):
        self.assertEqual(API['classify'](['local', 'localhost'])['nonempty_nonzero'], 2)


if __name__ == '__main__':
    unittest.main()
