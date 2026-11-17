"""Exercise bounded supplier loading without loading real modules."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class SupplierTests(unittest.TestCase):
    def test_exact_source_boundary(self):
        adapt = runpy.run_path(str(BASE / 'build-commercial-native-145.py'))['adapt']
        source = '#include "native-media-bindings-141.h"\nnative_media136_load();'
        result = adapt(source)
        self.assertEqual(result.count('native_media145_load();'), 1)
        self.assertLess(result.index('native_media145_load();'), result.index('native_media136_load();'))
        with self.assertRaises(AssertionError):
            adapt(source + source)

    def test_budget_timeout_presence_and_clock(self):
        source = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static unsigned calls;
static int mode;
static double tick = 100;
static double native_media136_now(void) { tick += 0.01; return mode == 4 ? -1 : tick; }
static int fixture_access(const char *p, int flags) {
    assert(!strncmp(p, "/sys/module/", 12) && flags == F_OK);
    errno = ENOENT; return mode == 5 ? 0 : -1;
}
static int probe(const char *name, char *const args[], unsigned timeout) {
    assert(timeout == 4 && !strcmp(args[0], "/sbin/modprobe"));
    assert(!strcmp(args[1], "--config") && !strcmp(args[2], "/etc/modprobe.d"));
    assert(!strcmp(args[3], name) && !args[4]); ++calls;
    if (mode == 3) tick += 9;
    return mode == 1 ? 124 : mode == 2 ? 125 : 0;
}
#define access fixture_access
#include "native-media-suppliers-145.h"
int main(int argc, char **argv) {
    assert(argc == 2); mode = atoi(argv[1]); native_media145_load();
    assert(calls == (mode == 0 ? 2 : mode <= 3 ? 1 : 0)); return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='supplier145-test-') as directory:
            binary = Path(directory) / 'test'
            subprocess.run(['cc', '-x', 'c', '-', '-I', str(BASE), '-std=c11', '-Wall', '-Wextra',
                            '-Werror', '-o', str(binary)], input=source, text=True, check=True)
            for mode in range(6):
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, check=True)
                self.assertIn('MEDIA145_SUPPLIERS_END hardware_success_not_inferred=1', result.stdout)


if __name__ == '__main__':
    unittest.main()
