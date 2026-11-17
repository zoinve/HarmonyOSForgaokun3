"""Verify module admission and timeout behavior without loading any module."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class MediaTests(unittest.TestCase):
    def test_exact_original_service_boundary(self):
        adapt = runpy.run_path(str(BASE / 'build-commercial-native-136.py'))['adapt']
        original = ('before\n#include "native-driver-observer-133.h"\n'
                    '    native_driver_observer133("services_sample");\n'
                    '                network081_netifs();\n                native_original();\nafter')
        result = adapt(original)
        self.assertTrue(result.startswith('before\n'))
        self.assertTrue(result.endswith('\nafter'))
        self.assertEqual(result.count('native_media136_load();'), 1)
        self.assertEqual(result.count('native_media136_observe('), 2)
        self.assertLess(result.index('native_media136_load();'), result.index('native_original();'))
        self.assertIn('native_driver_observer133("services_sample");', result)
        for source in ['unknown', original + original]:
            with self.assertRaises(AssertionError):
                adapt(source)

    def test_budget_timeout_presence_and_clock_refusal(self):
        source = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include "native-driver-observer-133.h"
static double fixture_now = 100.0, fixture_step = 0.01;
static unsigned calls;
static int fixture_result, fixture_present, fixture_clock_failure;
static int probe(const char *, char *const[], unsigned);
static int access_fixture136(const char *path, int mode) {
    assert(!strncmp(path, "/sys/module/", 12)); assert(mode == F_OK);
    errno = ENOENT;
    return fixture_present ? 0 : -1;
}
static int clock_fixture136(clockid_t clock, struct timespec *now) {
    assert(clock == CLOCK_MONOTONIC);
    if (fixture_clock_failure) { errno = EIO; return -1; }
    now->tv_sec = (time_t)fixture_now;
    now->tv_nsec = (long)((fixture_now - now->tv_sec) * 1e9);
    return 0;
}
#define access access_fixture136
#define clock_gettime clock_fixture136
#include "native-media-136.h"
#undef access
#undef clock_gettime
static int probe(const char *name, char *const args[], unsigned timeout) {
    assert(timeout == 4);
    assert(!strcmp(args[0], "/sbin/modprobe"));
    assert(!strcmp(args[1], "--config"));
    assert(!strcmp(args[2], "/etc/modprobe.d"));
    assert(!strcmp(args[3], name) && args[4] == NULL);
    assert(!strcmp(name, native_media136_modules[calls]));
    ++calls; fixture_now += fixture_step;
    return fixture_result;
}
int main(int argc, char **argv) {
    assert(argc == 2);
    int mode = atoi(argv[1]);
    assert(native_media136_allowed(0, 0, 4));
    assert(native_media136_allowed(0, 26, 4));
    assert(!native_media136_allowed(0, 27, 4));
    assert(!native_media136_allowed(-1, 0, 4));
    assert(!native_media136_allowed(1, 0, 4));
    assert(!native_media136_allowed(0, NAN, 4));
    assert(!native_media136_allowed(0, 0, 0));
    if (mode == 1) fixture_result = 124;
    if (mode == 2) fixture_step = 4;
    if (mode == 3) fixture_clock_failure = 1;
    if (mode == 4) fixture_present = 1;
    if (mode == 99) {
        native_media136_observe("not_executed");
        native_driver_observer133("not_executed");
    }
    native_media136_load();
    if (mode == 0) assert(calls == 18);
    if (mode == 1) assert(calls == 1);
    if (mode == 2) assert(calls == 7);
    if (mode == 3 || mode == 4) assert(calls == 0);
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='media136-test-') as directory:
            binary = Path(directory) / 'test'
            subprocess.run(['cc', '-x', 'c', '-', '-I', str(BASE), '-std=c11',
                            '-Wall', '-Wextra', '-Werror', '-o', str(binary)], input=source, text=True, check=True)
            for mode in range(5):
                result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True, check=True)
                self.assertIn('MEDIA136_LOAD_END hardware_success_not_inferred=1', result.stdout)
                if mode == 1:
                    self.assertIn('reason=probe_timeout_or_refusal no_retry=1', result.stdout)
                if mode in [2, 3]:
                    self.assertIn('reason=group_budget no_retry=1', result.stdout)


if __name__ == '__main__':
    unittest.main()
