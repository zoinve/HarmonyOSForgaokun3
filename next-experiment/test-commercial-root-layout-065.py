"""Run the exact layout helper against mocked syscalls, never the real root."""
from pathlib import Path
import runpy
import re
import subprocess
import tempfile
import unittest

B = Path(__file__).resolve().parent
layout = runpy.run_path(str(B / 'commercial-root-layout-065.py'))
PRELUDE = r'''
#include <assert.h>
#include <errno.h>
#include <setjmp.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
static jmp_buf escape;
static int scenario,links;
static void fail(const char *message) { assert(message); longjmp(escape,1); }
static ssize_t fake_readlink(const char *path,char *buffer,size_t length)
{
    assert(!strcmp(path,"/usr/chipset") && length>=7);
    memcpy(buffer,scenario==1?"/wrong!":"/vendor",7);return 7;
}
static int fake_lstat(const char *path,struct stat *st)
{
    assert(!strcmp(path,"/chipset"));memset(st,0,sizeof(*st));
    if(scenario==2)return 0;
    errno=ENOENT;return -1;
}
static int fake_symlink(const char *target,const char *path)
{
    assert(!strcmp(target,"/vendor") && !strcmp(path,"/chipset"));++links;
    if(scenario==3){errno=EPERM;return -1;}return 0;
}
static int fake_stat(const char *path,struct stat *st)
{
    assert(!strcmp(path,"/chipset/etc/param") || !strcmp(path,"/vendor/etc/param"));
    if(scenario==4){errno=ENOENT;return -1;}
    memset(st,0,sizeof(*st));st->st_dev=5;st->st_ino=7;st->st_mode=S_IFDIR|0755;
    if(scenario==5 && !strcmp(path,"/vendor/etc/param"))st->st_ino=8;
    if(scenario==6)st->st_mode=S_IFREG|0644;
    return 0;
}
static int fake_dprintf(int fd,const char *format,...){assert(fd==1 && format);return 0;}
#define readlink fake_readlink
#define lstat fake_lstat
#define symlink fake_symlink
#define stat fake_stat
#define dprintf fake_dprintf
'''
SUFFIX = r'''
int main(void)
{
    for(scenario=0;scenario<=6;++scenario){
        links=0;
        if(!setjmp(escape)){
            commercial_original_layout065();assert(scenario==0 && links==1);
        }else{assert(scenario!=0);if(scenario<=2)assert(links==0);}
    }
    puts("PASS: exact original link, existing-path refusal, syscall errors and directory identity checks");
    return 0;
}
'''


class Tests(unittest.TestCase):
    def test_exact_source_delta(self):
        previous = runpy.run_path(str(B / 'build-commercial-native-064.py'))['inner']
        updated = layout['repair'](previous)
        self.assertEqual(updated.replace(layout['FIX'] + '\n', '', 1).replace(layout['CALL'], '', 1), previous)
        for forbidden in ['chmod', 'chown', 'setuid', 'setgid', 'param set', 'memcpy']:
            self.assertNotIn(forbidden, layout['FIX'])

    def test_syscall_guards(self):
        # Limit macro replacement to function invocations, not struct stat tags.
        helper = layout['FIX']
        for name in ['readlink', 'lstat', 'symlink', 'stat', 'dprintf']:
            helper = re.sub(r'\b' + name + r'\(', 'fake_' + name + '(', helper)
        prelude = PRELUDE[:PRELUDE.index('#define readlink')]
        with tempfile.TemporaryDirectory(prefix='commercial-layout065-') as temporary:
            source = Path(temporary) / 'test.c'
            source.write_text(prelude + helper + SUFFIX)
            binary = Path(temporary) / 'test'
            subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    unittest.main()
