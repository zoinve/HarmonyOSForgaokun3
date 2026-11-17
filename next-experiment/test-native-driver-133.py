"""Exercise read-only observer errors and exact source transformations."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class DriverTests(unittest.TestCase):
    def test_only_real_registration_name_changes(self):
        adapt = runpy.run_path(str(BASE / 'build-commercial-battery-module-132.py'))['adapt']
        original = 'before\n.name\t\t\t= "gaokun-ec-battery",\nafter'
        result = adapt(original)
        self.assertEqual(result.replace('"battery"', '"gaokun-ec-battery"'), original)
        for source in ['unknown', original + original]:
            with self.assertRaises(AssertionError):
                adapt(source)

    def test_outer_delta_is_bounded_and_observation_only(self):
        adapt = runpy.run_path(str(BASE / 'build-commercial-native-133.py'))['adapt']
        source = ('if(probe("oobe-seed-load123",seed123,12))okay=0;\n'
                  '#include "native-backlight-permissions-130.h"\n'
                  '    network081_kmsg();\n    network081_netifs();\n'
                  '    if(okay && native_backlight_permissions130()){')
        result = adapt(source)
        self.assertIn('seed123,36)', result)
        self.assertEqual(result.count('native_driver_observer133('), 2)
        self.assertIn('before_services', result)
        self.assertNotIn('seed123,12)', result)
        with self.assertRaises(AssertionError):
            adapt('unknown baseline')

    def test_observer_missing_zero_symlink_overflow_and_non_sysfs(self):
        source = r'''
#define _GNU_SOURCE
#include "native-driver-observer-133.h"
int main(int argc, char **argv) {
    if (argc < 3) return 2;
    if (argc == 99) native_driver_observer133("unused");
    const char *attributes[] = {"capacity", "current_now", "temp", "linked", "long", "empty"};
    if (!strcmp(argv[1], "directory"))
        native_driver133_directory("fixture", 1234, argv[2], attributes, 6);
    else {
        int dir = open(argv[2], O_RDONLY | O_DIRECTORY | O_CLOEXEC);
        if (dir < 0) return 3;
        for (size_t i = 0; i < 6; ++i)
            native_driver133_attribute("fixture", 1234, argv[2], dir, attributes[i]);
        close(dir);
    }
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='driver133-') as directory:
            root = Path(directory)
            binary = root / 'test'
            subprocess.run(['cc', '-x', 'c', '-', '-I', str(BASE), '-std=c11',
                            '-Wall', '-Wextra', '-Werror', '-o', str(binary)], input=source, text=True, check=True)
            (root / 'capacity').write_text('98\n')
            (root / 'current_now').write_text('0\n')
            (root / 'linked').symlink_to(root / 'capacity')
            (root / 'long').write_text('1' * 256)
            (root / 'empty').write_text('\n')
            result = subprocess.check_output([str(binary), 'attributes', str(root)], text=True)
            self.assertIn('attr=capacity valid=1 value=98', result)
            self.assertIn('attr=current_now valid=1 value=0', result)
            for name in ['temp', 'linked', 'long', 'empty']:
                self.assertIn('attr=' + name + ' valid=0 errno=', result)
                self.assertNotIn('attr=' + name + ' valid=1', result)
            refused = subprocess.check_output([str(binary), 'directory', str(root)], text=True)
            self.assertIn('GAOKUN_DRIVER133_REFUSED', refused)
            self.assertNotIn('valid=1', refused)
            self.assertEqual((root / 'capacity').read_text(), '98\n')
            self.assertFalse((root / 'temp').exists())


if __name__ == '__main__':
    unittest.main()
