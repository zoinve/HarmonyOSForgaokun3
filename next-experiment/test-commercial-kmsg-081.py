"""Compile the exact C reader with mocked read/open; never touch real kmsg."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

LOGGER = runpy.run_path(str(Path(__file__).with_name('build-commercial-native-081.py')))['LOGGER']
STUB = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static int scenario, opens, reads;
static int mock_open(const char *path, int flags, ...)
{
    ++opens;
    assert(!strcmp(path, "/dev/kmsg"));
    assert((flags & (O_NONBLOCK | O_CLOEXEC)) == (O_NONBLOCK | O_CLOEXEC));
    assert(!(flags & (O_WRONLY | O_RDWR | O_CREAT | O_TRUNC)));
    if (scenario == 5) { errno = EACCES; return -1; }
    return 42;
}
static ssize_t mock_read(int fd, void *buffer, size_t size)
{
    assert(fd == 42 && size == 8192);
    ++reads;
    if (scenario == 2 || (scenario == 1 && reads == 1)) { errno = EPIPE; return -1; }
    if (scenario == 7) { errno = EIO; return -1; }
    if (scenario == 4) { memset(buffer, 'x', 4096); return 4096; }
    if (scenario == 3) { memcpy(buffer, "unrelated", 9); return 9; }
    if (reads == 1 || (scenario == 1 && reads == 2)) {
        const char *record = "6,12,123000,-;ath11k_pci fw_version 0x1\n";
        size_t bytes = strlen(record);
        memcpy(buffer, record, bytes);
        return (ssize_t)bytes;
    }
    errno = EAGAIN;
    return -1;
}
#define open mock_open
#define read mock_read
'''
MAIN = r'''
int main(int argc, char **argv)
{
    scenario = argc > 1 ? atoi(argv[1]) : 0;
    network081_kmsg();
    if (scenario == 6) network081_kmsg();
    printf("MOCK opens=%d reads=%d\n", opens, reads);
    return 0;
}
'''


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        source = root / 'reader.c'
        source.write_text(STUB + LOGGER + MAIN)
        cls.exe = root / 'reader'
        subprocess.run(['gcc', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(cls.exe)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_case(self, scenario):
        return subprocess.run([str(self.exe), str(scenario)], check=True, capture_output=True, text=True, timeout=3).stdout

    def test_record_preserved_and_eagain_reported(self):
        out = self.run_case(0)
        self.assertIn('6,12,123000,-;ath11k_pci fw_version 0x1', out)
        self.assertIn('selected=1 losses=0 errno=11', out)

    def test_overrun_reported_then_read_continues(self):
        self.assertIn('selected=1 losses=1 errno=11', self.run_case(1))

    def test_repeated_overrun_is_bounded(self):
        out = self.run_case(2)
        self.assertIn('losses=5 errno=32', out)
        self.assertIn('reads=5', out)

    def test_record_count_bound(self):
        self.assertIn('records=512 bytes=4608 selected=0', self.run_case(3))

    def test_byte_count_bound(self):
        self.assertIn('records=32 bytes=131072', self.run_case(4))

    def test_open_permission_error_is_not_ignored(self):
        out = self.run_case(5)
        self.assertIn('OPEN_FAILED errno=13', out)
        self.assertIn('reads=0', out)

    def test_private_cursor_reused_without_reopen(self):
        self.assertIn('MOCK opens=1 reads=3', self.run_case(6))

    def test_unexpected_read_error_stops(self):
        self.assertIn('selected=0 losses=0 errno=5', self.run_case(7))


if __name__ == '__main__':
    unittest.main()
