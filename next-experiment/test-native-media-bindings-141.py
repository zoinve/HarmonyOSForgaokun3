"""Mock all debugfs operations; tests never mount or modify target state."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class Binding141Tests(unittest.TestCase):
    def test_exact_source_boundary(self):
        adapt = runpy.run_path(str(BASE / 'build-commercial-native-141.py'))['adapt']
        source = ('#include "native-media-bindings-139.h"\n'
                  'native_media136_load();\n'
                  'native_media139_observe("services_sample136");\n'
                  'native_media139_observe("before_services136");')
        result = adapt(source)
        self.assertEqual(result.count('native_media141_prepare();'), 1)
        self.assertLess(result.index('native_media141_prepare();'), result.index('native_media136_load();'))
        self.assertEqual(result.count('native_media141_observe('), 2)
        with self.assertRaises(AssertionError):
            adapt(source + source)

    def test_debugfs_guards_and_sampling(self):
        source = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/vfs.h>
static int mode, mounts, directories, buses;
static double tick;
static int fixture_statfs(const char *p, struct statfs *s) {
    assert(!strcmp(p, "/sys/kernel/debug")); s->f_type = mode == 1 ? 0x64626720 : 0x1234;
    return 0;
}
static int fixture_mkdir(const char *p, mode_t m) {
    assert(!strcmp(p, "/sys/kernel/debug") && m == 0755); ++directories;
    errno = mode == 2 ? EACCES : EEXIST; return -1;
}
static int fixture_mount(const char *a, const char *p, const char *fs, unsigned long flags, const void *data) {
    assert(!strcmp(a, "debugfs") && !strcmp(p, "/sys/kernel/debug") && !strcmp(fs, "debugfs"));
    assert(flags == (MS_NOSUID | MS_NODEV | MS_NOEXEC) && !data); ++mounts;
    errno = mode == 3 ? EPERM : 0; return mode == 3 ? -1 : 0;
}
static double native_media136_now(void) { return tick; }
static void native_media139_bus(const char *s, long long t, const char *p) {
    assert(!strcmp(s, "fixture") && t >= 0 && !strcmp(p, "/sys/bus/aprbus/devices")); ++buses;
}
#define statfs(path, result) fixture_statfs(path, result)
#define mkdir fixture_mkdir
#define mount fixture_mount
#include "native-media-bindings-141.h"
int main(int argc, char **argv) {
    assert(argc == 2); mode = atoi(argv[1]); errno = EDOM;
    native_media141_prepare(); assert(errno == EDOM);
    assert(mounts == ((mode == 0 || mode == 3) ? 1 : 0));
    assert(directories == (mode == 1 ? 0 : 1));
    tick = 10; native_media141_observe("fixture"); assert(buses == 1);
    tick = 11; native_media141_observe("fixture"); assert(buses == 1);
    tick = -1; native_media141_observe("fixture"); assert(buses == 1);
    tick = 30; native_media141_observe("fixture"); assert(buses == 2);
    assert(errno == EDOM); return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='bindings141-test-') as directory:
            binary = Path(directory) / 'test'
            subprocess.run(['cc', '-x', 'c', '-', '-I', str(BASE), '-std=c11', '-Wall', '-Wextra',
                            '-Werror', '-o', str(binary)], input=source, text=True, check=True)
            for mode in range(4):
                subprocess.run([str(binary), str(mode)], capture_output=True, check=True)


if __name__ == '__main__':
    unittest.main()
