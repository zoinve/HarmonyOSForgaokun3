from pathlib import Path
import runpy
import unittest

resolve = runpy.run_path(str(Path(__file__).with_name('audit-usb-implementation-150.py')))['resolve']


class LinkTests(unittest.TestCase):
    def test_fast_and_long_link(self):
        values = {
            'stat /lib64/one.so': b'Type: symlink\nFast link dest: "two.so"\n',
            'stat /lib64/two.so': b'Type: symlink\n',
            'cat /lib64/two.so': b'/system/lib64/three.so',
            'stat /system/lib64/three.so': b'Type: regular\n',
            'cat /system/lib64/three.so': b'\x7fELFtest',
        }
        target, data, links = resolve(lambda image, command, optional: values[command], '/vendor/lib64/one.so')
        self.assertEqual(target, '/system/lib64/three.so')
        self.assertEqual(data, b'\x7fELFtest')
        self.assertEqual(len(links), 2)

    def test_escape_refused(self):
        def read(image, command, optional):
            return b'Fast link dest: "/data/private.so"\n' if command.startswith('stat ') else b''
        with self.assertRaises(ValueError):
            resolve(read, '/vendor/lib64/one.so')

    def test_cycle_refused(self):
        with self.assertRaises(AssertionError):
            resolve(lambda image, command, optional: b'Fast link dest: "one.so"\n', '/vendor/lib64/one.so')


if __name__ == '__main__':
    unittest.main()
