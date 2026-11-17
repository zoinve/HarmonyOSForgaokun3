"""Exercise the exact helper with mocked namespace syscalls, never host setns."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name('network-namespace-observe-082.c').read_text()
STUB = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
static int scenario, opened, joined, executed;
static int mock_open(const char *path, int flags, ...)
{
    assert(flags == (O_RDONLY | O_CLOEXEC));
    ++opened;
    assert(!strcmp(path, opened == 1 ? "/proc/self/ns/net" : "/proc/404/ns/net"));
    if (scenario == 1 && opened == 2) { errno = EACCES; return -1; }
    return opened + 10;
}
static int mock_fstat(int fd, struct stat *out)
{
    memset(out, 0, sizeof(*out)); out->st_dev = 7;
    out->st_ino = (fd == 11 || scenario == 2) ? 100 : 200;
    return 0;
}
static int mock_stat(const char *path, struct stat *out)
{
    assert(!strcmp(path, "/proc/self/ns/net") && joined == 1);
    memset(out, 0, sizeof(*out)); out->st_dev = 7;
    out->st_ino = scenario == 4 ? 300 : 200;
    return 0;
}
static int mock_setns(int fd, int kind)
{
    assert(fd == 12 && kind == CLONE_NEWNET); ++joined;
    if (scenario == 3) { errno = EPERM; return -1; }
    return 0;
}
static int mock_close(int fd) { assert(fd == 11 || fd == 12); return 0; }
static int mock_execv(const char *path, char *const args[])
{
    assert(joined == 1);
    assert(!strcmp(path, "/network082/lib/ld-linux-aarch64.so.1"));
    assert(!strcmp(args[1], "--library-path"));
    assert(!strcmp(args[2], "/network082/usr/lib/aarch64-linux-gnu"));
    assert(!strcmp(args[3], "/network082/usr/sbin/iw"));
    assert(!strcmp(args[4], "dev") && args[5] == NULL);
    ++executed; errno = ENOENT; return -1;
}
#define open(...) mock_open(__VA_ARGS__)
#define fstat(...) mock_fstat(__VA_ARGS__)
#define stat(...) mock_stat(__VA_ARGS__)
#define setns(...) mock_setns(__VA_ARGS__)
#define close(...) mock_close(__VA_ARGS__)
#define execv(...) mock_execv(__VA_ARGS__)
'''
MAIN = r'''
int main(int argc, char **argv)
{
    scenario = argc > 1 ? atoi(argv[1]) : 0;
    char *input[] = {"observer", argc > 2 ? argv[2] : "404", NULL};
    int rc = observe_main(2, input);
    printf("RESULT rc=%d opened=%d joined=%d executed=%d\n", rc, opened, joined, executed);
    return 0;
}
'''


class NamespaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        source = Path(cls.temp.name) / 'test.c'
        source.write_text(STUB + SOURCE.replace('int main(', 'int observe_main(', 1) + MAIN)
        cls.exe = Path(cls.temp.name) / 'test'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(cls.exe)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def case(self, scenario, pid='404'):
        return subprocess.run([str(self.exe), str(scenario), pid], capture_output=True, text=True, check=True, timeout=3).stdout

    def test_bad_pid_has_no_syscalls(self):
        for pid in ('0', '1', '-1', '404x', '', '2147483648'):
            self.assertIn('rc=64 opened=0 joined=0 executed=0', self.case(0, pid))

    def test_permission_error_does_not_join(self):
        self.assertIn('rc=71 opened=2 joined=0 executed=0', self.case(1))

    def test_same_namespace_is_refused(self):
        self.assertIn('rc=72 opened=2 joined=0 executed=0', self.case(2))

    def test_setns_permission_error_does_not_exec(self):
        self.assertIn('rc=73 opened=2 joined=1 executed=0', self.case(3))

    def test_identity_mismatch_does_not_exec(self):
        self.assertIn('rc=74 opened=2 joined=1 executed=0', self.case(4))

    def test_verified_namespace_execs_only_readonly_iw_dev(self):
        output = self.case(0)
        self.assertIn('NETWORK082_NAMESPACE_JOINED pid=404', output)
        self.assertIn('rc=75 opened=2 joined=1 executed=1', output)


if __name__ == '__main__':
    unittest.main()
