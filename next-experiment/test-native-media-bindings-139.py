"""Exercise diagnostic sampling bounds and absent/bound driver observations."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class BindingTests(unittest.TestCase):
    def test_source_boundary(self):
        adapt = runpy.run_path(str(BASE / 'build-commercial-native-139.py'))['adapt']
        original = ('before\n#include "native-media-136.h"\n'
                    'native_media136_observe("services_sample136");\n'
                    'native_media136_observe("before_services136");\nafter')
        result = adapt(original)
        self.assertEqual(result.count('native_media139_observe('), 2)
        self.assertIn('native_media136_observe("services_sample136");', result)
        self.assertTrue(result.startswith('before\n') and result.endswith('\nafter'))
        with self.assertRaises(AssertionError):
            adapt(original + original)

    def test_read_only_bindings_and_rate_limit(self):
        source = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
static double tick;
static unsigned streams, attributes;
static double native_media136_now(void) { return tick; }
static void native_media136_stream(const char *stage, const char *path, unsigned limit) {
    assert(!strcmp(stage, "fixture"));
    assert(!strcmp(path, "/sys/kernel/debug/devices_deferred"));
    assert(limit == 16384); ++streams;
}
static void native_driver133_directory(const char *stage, long long mono, const char *path,
                                      const char *const *attrs, size_t count) {
    assert(!strcmp(stage, "fixture")); assert(mono >= 0); assert(path[0] == '/');
    assert(count == 1 && !strcmp(attrs[0], "modalias")); ++attributes;
}
#include "native-media-bindings-139.h"
int main(int argc, char **argv) {
    assert(argc == 2);
    native_media139_bus("fixture", 0, argv[1]);
    assert(attributes == 2);
    errno = EDOM; tick = 10; native_media139_observe("fixture");
    assert(errno == EDOM && streams == 1);
    tick = 15; native_media139_observe("fixture"); assert(streams == 1);
    tick = 30; native_media139_observe("fixture"); assert(streams == 2);
    tick = 29; native_media139_observe("fixture"); assert(streams == 2);
    tick = -1; native_media139_observe("fixture"); assert(streams == 2);
    tick = 51; native_media139_observe("fixture"); assert(streams == 3);
    assert(errno == EDOM);
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='bindings139-test-') as directory:
            root = Path(directory)
            bus = root / 'bus'
            bus.mkdir()
            (bus / 'bound').mkdir()
            (bus / 'unbound').mkdir()
            (bus / 'bound/driver').symlink_to('/fixture/drivers/snd-sc8280xp')
            binary = root / 'test'
            subprocess.run(['cc', '-x', 'c', '-', '-I', str(BASE), '-std=c11',
                            '-Wall', '-Wextra', '-Werror', '-o', str(binary)], input=source, text=True, check=True)
            result = subprocess.run([str(binary), str(bus)], capture_output=True, text=True, check=True)
            self.assertIn('driver=snd-sc8280xp errno=0', result.stdout)
            self.assertIn('driver=absent errno=2', result.stdout)
            self.assertEqual(result.stdout.count('MEDIA139_BINDINGS_BEGIN'), 3)


if __name__ == '__main__':
    unittest.main()
