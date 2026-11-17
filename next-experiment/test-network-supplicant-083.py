"""Test exact fixed commands with mocked effects; never launch a host daemon."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).with_name('network-supplicant-083.c').read_text()
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
#include <sys/vfs.h>
#include <sys/wait.h>
#include <unistd.h>
static int scenario, mutations, executed, reads, written;
static int mock_mkdir(const char *path, mode_t mode)
{ assert(!strcmp(path,"/data/local/tmp/wpa_ctrl") && mode==0770); ++mutations; return 0; }
static int mock_chown(const char *path, uid_t uid, gid_t gid)
{ assert(!strcmp(path,"/data/local/tmp/wpa_ctrl") && uid==0 && gid==1010); ++mutations; return 0; }
static int mock_chmod(const char *path, mode_t mode)
{ assert(!strcmp(path,"/data/local/tmp/wpa_ctrl") && mode==0770); ++mutations; return 0; }
static int mock_lstat(const char *path, struct stat *out)
{
    assert(!strcmp(path,"/data/local/tmp") || !strcmp(path,"/data/local/tmp/wpa_ctrl"));
    memset(out,0,sizeof(*out)); out->st_mode=scenario==2 ? S_IFLNK : S_IFDIR; return 0;
}
static int mock_statfs(const char *path, struct statfs *out)
{ assert(!strcmp(path,"/data")); memset(out,0,sizeof(*out)); out->f_type=scenario==1 ? 0x01021994 : 0xef53; return 0; }
static int mock_execv(const char *path, char *const args[])
{
    assert(!strcmp(path,"/network083/lib/ld-linux-aarch64.so.1"));
    assert(!strcmp(args[1],"--library-path"));
    assert(!strcmp(args[2],"/network083/usr/lib/aarch64-linux-gnu"));
    if (!strcmp(args[3],"/network083/usr/sbin/wpa_supplicant")) {
        assert(!strcmp(args[4],"-B") && !strcmp(args[5],"-Dnl80211"));
        assert(!strcmp(args[6],"-iwlan0") && !strcmp(args[7],"-c/network083/wpa.conf"));
        assert(!strcmp(args[8],"-P/data/local/tmp/wpa_ctrl/supplicant.pid"));
        assert(!strcmp(args[9],"-f/data/local/tmp/wpa_ctrl/supplicant.log") && !args[10]);
    } else {
        assert(!strcmp(args[3],"/network083/usr/sbin/wpa_cli"));
        assert(!strcmp(args[4],"-p") && !strcmp(args[5],"/data/local/tmp/wpa_ctrl"));
        assert(!strcmp(args[6],"-i") && !strcmp(args[7],"wlan0") && !args[9]);
        assert(!strcmp(args[8],"ping") || !strcmp(args[8],"scan") ||
               !strcmp(args[8],"scan_results") || !strcmp(args[8],"status"));
    }
    ++executed; errno=ENOENT; return -1;
}
static int mock_open(const char *path, int flags, ...)
{
    assert(!strcmp(path,"/data/local/tmp/wpa_ctrl/supplicant.log"));
    assert(flags==(O_RDONLY|O_CLOEXEC|O_NOFOLLOW));
    if(scenario==3){errno=ENOENT;return -1;} return 42;
}
static ssize_t mock_read(int fd, void *buffer, size_t size)
{
    assert(fd==42 && size==4096); ++reads;
    if(scenario==5){errno=EIO;return -1;}
    if(scenario!=4 && reads>1)return 0;
    memset(buffer,'x',size);return (ssize_t)size;
}
static ssize_t mock_write(int fd,const void *buffer,size_t size)
{ assert(fd==1 && buffer); written+=(int)size;return (ssize_t)size; }
static int mock_close(int fd){assert(fd==42);return 0;}
#define mkdir(...) mock_mkdir(__VA_ARGS__)
#define chown(...) mock_chown(__VA_ARGS__)
#define chmod(...) mock_chmod(__VA_ARGS__)
#define lstat(...) mock_lstat(__VA_ARGS__)
#define statfs(...) mock_statfs(__VA_ARGS__)
#define execv(...) mock_execv(__VA_ARGS__)
#define open(...) mock_open(__VA_ARGS__)
#define read(...) mock_read(__VA_ARGS__)
#define write(...) mock_write(__VA_ARGS__)
#define close(...) mock_close(__VA_ARGS__)
'''
MAIN = r'''
int main(int argc,char **argv)
{
    assert(argc==3); scenario=atoi(argv[1]);
    int rc=mode_valid(argv[2]) ? run_mode(argv[2]) : 64;
    printf("RESULT rc=%d mutations=%d executed=%d reads=%d written=%d\n",rc,mutations,executed,reads,written);
    return 0;
}
'''


class CommandTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        source = root / 'test.c'
        source.write_text(STUB + SOURCE.replace('int main(', 'int target_main(', 1) + MAIN)
        cls.exe = root / 'test'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(cls.exe)], capture_output=True, check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def case(self, mode, scenario=0):
        return subprocess.run([str(self.exe), str(scenario), mode], check=True, capture_output=True, text=True, timeout=3).stdout

    def test_start_exact_blank_config_and_no_keys_logging(self):
        self.assertIn('rc=86 mutations=3 executed=1', self.case('start'))

    def test_wrong_data_filesystem_refused(self):
        self.assertIn('rc=83 mutations=0 executed=0', self.case('start', 1))

    def test_symlink_parent_refused(self):
        self.assertIn('rc=83 mutations=0 executed=0', self.case('start', 2))

    def test_fixed_query_commands_have_no_mutations(self):
        for mode in ('ping', 'scan', 'scan_results', 'status'):
            self.assertIn('rc=86 mutations=0 executed=1', self.case(mode))

    def test_arbitrary_control_commands_rejected(self):
        for mode in ('SET_NETWORK', 'terminate', 'reconnect', 'add_network', 'status;id'):
            self.assertIn('rc=64 mutations=0 executed=0', self.case(mode))

    def test_log_dump_readonly_and_bounded(self):
        self.assertIn('rc=0 mutations=0 executed=0 reads=16 written=65536', self.case('log', 4))

    def test_log_read_errors_reported(self):
        self.assertIn('rc=80', self.case('log', 3))
        self.assertIn('rc=81', self.case('log', 5))


if __name__ == '__main__':
    unittest.main()
