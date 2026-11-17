from pathlib import Path
import runpy
import tempfile
import unittest

API = runpy.run_path(str(Path(__file__).with_name('complete-settings-state-labels-190.py')))


class Tests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        policy = Path(folder.name) / 'contexts'
        with policy.open('x') as stream:
            stream.write('/data/app(/.*)? u:object_r:fixture_app:s0\n')
        self.policy = API['FilePolicy'](policy)
        self.addCleanup(self.policy.close)

    def test_real_libselinux_lookup(self):
        self.assertEqual(self.policy.lookup('/data/app/fixture/resources.index', 0o100644),
                         'u:object_r:fixture_app:s0')

    def test_unmatched_path_fails(self):
        with self.assertRaises(OSError):
            self.policy.lookup('/data/service/unknown', 0o100644)

    def test_outside_data_rejected(self):
        with self.assertRaises(AssertionError):
            self.policy.lookup('/etc/shadow', 0o100600)
        with self.assertRaises(AssertionError):
            self.policy.lookup('/data/app/../../etc/shadow', 0o100600)


if __name__ == '__main__':
    unittest.main()
