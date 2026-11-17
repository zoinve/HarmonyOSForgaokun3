"""Archive hierarchy regression; no device access or operational test."""
from pathlib import Path
import runpy, stat, unittest
base=Path(__file__).resolve().parent
assert (base/'commercial-archive-017.py').is_file(), 'missing explicit initramfs parent-directory repair'
repair=runpy.run_path(str(base/'commercial-archive-017.py'))['complete']
class Hierarchy(unittest.TestCase):
    def test_missing_parents_are_explicit_and_precede_file(self):
        name='native-target/graphics016/vendor/lib64/driver.so'
        original={'native-target':(stat.S_IFDIR|0o755,b''),name:(stat.S_IFREG|0o644,b'actual hardware bytes')}
        result=repair(original)
        self.assertEqual(result[name],original[name]);self.assertEqual(len(original),2)
        for parent in ['native-target/graphics016','native-target/graphics016/vendor','native-target/graphics016/vendor/lib64']:
            self.assertEqual(result[parent],(stat.S_IFDIR|0o755,b''))
            self.assertLess(sorted(result).index(parent),sorted(result).index(name))
        self.assertEqual(repair(result),result)
    def test_existing_non_directory_parent_is_rejected(self):
        with self.assertRaises(AssertionError):
            repair({'native-target':(stat.S_IFDIR|0o755,b''),'native-target/graphics016':(stat.S_IFLNK|0o777,b'/outside'),'native-target/graphics016/a':(stat.S_IFREG|0o644,b'x')})
if __name__=='__main__':unittest.main()
