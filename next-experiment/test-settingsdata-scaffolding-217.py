"""Exercise the preservation comparison used by the local directory repair."""
import os
from pathlib import Path
import runpy
import tempfile
import unittest

fingerprint = runpy.run_path(str(Path(__file__).with_name('prepare-settingsdata-scaffolding-215.py')))['fingerprint']


class PreservationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.file = self.root / 'existing.db'
        self.file.write_bytes(b'unchanged genuine database bytes')
        self.before = fingerprint(self.root, set())

    def test_detects_file_bytes(self):
        self.file.write_bytes(b'changed')
        self.assertNotEqual(self.before, fingerprint(self.root, set()))

    def test_detects_mode(self):
        self.file.chmod(0o600 if self.file.stat().st_mode & 0o777 != 0o600 else 0o640)
        self.assertNotEqual(self.before, fingerprint(self.root, set()))

    def test_detects_xattr(self):
        os.setxattr(self.file, 'user.preservation_test', b'changed')
        self.assertNotEqual(self.before, fingerprint(self.root, set()))

    def test_detects_added_file_under_excluded_directory(self):
        new = self.root / 'new'
        new.mkdir()
        (new / 'unexpected.db').write_bytes(b'not an empty scaffold')
        self.assertNotEqual(self.before, fingerprint(self.root, {'new'}))

    def test_allows_only_named_empty_directories(self):
        (self.root / 'new').mkdir()
        (self.root / 'new' / 'nested').mkdir()
        self.assertEqual(self.before, fingerprint(self.root, {'new', 'new/nested'}))

    def test_does_not_follow_symlink(self):
        (self.root / 'link').symlink_to('/nonexistent-outside-tree')
        first = fingerprint(self.root, set())
        (self.root / 'link').unlink()
        (self.root / 'link').symlink_to('/different-outside-tree')
        self.assertNotEqual(first, fingerprint(self.root, set()))


if __name__ == '__main__':
    unittest.main()
