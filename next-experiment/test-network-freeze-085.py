"""Exercise the exact bounded freeze reader through mocked read-only syscalls."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

PROBE = runpy.run_path(str(Path(__file__).with_name('commercial-network-helper-085.py')))['PROBE']
STUB = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
static int scenario, opened, reads, bytes, enumerated, closed;
static struct dirent entry;
static int mock_open(const char *path,int flags,...)
{
    assert(!strcmp(path,"/data/log/eventlog/freeze"));
    assert(flags==(O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW));
    if(scenario==1){errno=ENOENT;return -1;}return 42;
}
static DIR *mock_fdopendir(int fd){assert(fd==42);return (DIR *)1;}
static int mock_dirfd(DIR *dir){assert(dir==(DIR *)1);return 42;}
static struct dirent *mock_readdir(DIR *dir)
{
    assert(dir==(DIR *)1);++enumerated;
    if(scenario!=5 && enumerated>20)return NULL;
    strcpy(entry.d_name,scenario==5 ? "unrelated" : "THREAD_BLOCK_3S_20261115_42_stack");
    return &entry;
}
static int mock_openat(int fd,const char *name,int flags,...)
{
    assert(fd==42 && !strcmp(name,entry.d_name));
    assert(flags==(O_RDONLY|O_CLOEXEC|O_NOFOLLOW));++opened;
    if(scenario==2){errno=ELOOP;return -1;}return 43;
}
static int mock_fstat(int fd,struct stat *out)
{
    assert(fd==43);memset(out,0,sizeof(*out));
    out->st_mode=scenario==3 ? S_IFSOCK : S_IFREG;out->st_size=131073;return 0;
}
static ssize_t mock_read(int fd,void *buffer,size_t size)
{assert(fd==43 && size==4096);++reads;memset(buffer,'x',size);return (ssize_t)size;}
static ssize_t mock_write(int fd,const void *buffer,size_t size)
{assert(fd==1 && buffer);bytes+=(int)size;return (ssize_t)size;}
static int mock_close(int fd){assert(fd==42 || fd==43);++closed;return 0;}
static int mock_closedir(DIR *dir){assert(dir==(DIR *)1);++closed;return 0;}
static int mock_execv(const char *path,char *const args[]){(void)path;(void)args;abort();}
#define open(...) mock_open(__VA_ARGS__)
#define fdopendir(...) mock_fdopendir(__VA_ARGS__)
#define dirfd(...) mock_dirfd(__VA_ARGS__)
#define readdir(...) mock_readdir(__VA_ARGS__)
#define openat(...) mock_openat(__VA_ARGS__)
#define fstat(...) mock_fstat(__VA_ARGS__)
#define read(...) mock_read(__VA_ARGS__)
#define write(...) mock_write(__VA_ARGS__)
#define close(...) mock_close(__VA_ARGS__)
#define closedir(...) mock_closedir(__VA_ARGS__)
#define execv(...) mock_execv(__VA_ARGS__)
'''
MAIN = r'''
int main(int argc,char **argv)
{
    assert(argc==2);scenario=atoi(argv[1]);
    if(scenario==99)return network085_probe("https");
    int rc=network085_freeze();
    printf("RESULT rc=%d opened=%d reads=%d bytes=%d enumerated=%d closed=%d\n",
        rc,opened,reads,bytes,enumerated,closed);return 0;
}
'''


class FreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        source = root / 'test.c'
        source.write_text(STUB + PROBE + MAIN)
        cls.exe = root / 'test'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(cls.exe)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def case(self, scenario):
        return subprocess.run([str(self.exe), str(scenario)], check=True, capture_output=True, text=True, timeout=3).stdout

    def test_files_and_bytes_bounded(self):
        self.assertIn('rc=0 opened=16 reads=512 bytes=2097152 enumerated=16 closed=17', self.case(0))

    def test_missing_directory_reported(self):
        self.assertIn('rc=88 opened=0 reads=0 bytes=0', self.case(1))

    def test_symlinks_refused(self):
        self.assertIn('rc=0 opened=20 reads=0 bytes=0', self.case(2))

    def test_nonregular_entries_not_read(self):
        self.assertIn('rc=0 opened=20 reads=0 bytes=0', self.case(3))

    def test_unrelated_files_not_opened_and_enumeration_bounded(self):
        self.assertIn('rc=0 opened=0 reads=0 bytes=0 enumerated=256 closed=1', self.case(5))


if __name__ == '__main__':
    unittest.main()
