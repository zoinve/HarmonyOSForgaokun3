"""Compile the real metadata/bootstrap header with bounded, non-hardware stubs."""
from pathlib import Path
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
FIXTURE = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
static int probes, timeout_probe, queries, closes, invalid_clock;
static double native_media136_now(void) { return invalid_clock ? -1 : 1; }
static int probe(const char *name, char *const args[], unsigned timeout) {
 assert(timeout==4); assert(!strcmp(args[0],"/sbin/modprobe"));
 assert(!strcmp(name,args[3])); ++probes; return timeout_probe ? 124 : 0;
}
static int read_text(const char *p,char *b,size_t n) { (void)p;(void)b;(void)n;return -1; }
static void native_driver133_directory(const char *s,long long t,const char *p,const char *const *a,size_t n) {
 (void)s;(void)t;(void)p;(void)a;(void)n;
}
static int mock_access(const char *p,int mode) { assert(mode==F_OK);assert(!strncmp(p,"/sys/module/",12));errno=ENOENT;return -1; }
static int mock_open(const char *p,int flags,...) {
 assert(!strcmp(p,"/dev/input/event42"));assert((flags&O_ACCMODE)==O_RDONLY);
 assert(flags&O_NONBLOCK);assert(flags&O_NOFOLLOW);return 7;
}
static int mock_fstat(int fd,struct stat *s) { assert(fd==7);memset(s,0,sizeof(*s));s->st_mode=S_IFCHR|0600;s->st_rdev=makedev(13,106);return 0; }
static int mock_close(int fd) { assert(fd==7);++closes;return 0; }
static int mock_ioctl(int fd,unsigned long request,...) {
 assert(fd==7);++queries;va_list args;va_start(args,request);void *out=va_arg(args,void *);va_end(args);
 if(request==EVIOCGBIT(EV_ABS,8)) { unsigned char *bits=out;memset(bits,0,8);bits[53/8]|=1U<<(53%8);return 8; }
 assert(request==EVIOCGABS(53));struct input_absinfo *a=out;
 *a=(struct input_absinfo){.value=1234,.minimum=0,.maximum=2559,.resolution=10};return 0;
}
#define access mock_access
#define open mock_open
#define fstat mock_fstat
#define close mock_close
#define ioctl mock_ioctl
#include "native-input-usb-148.h"
int main(void) {
 assert(native_input148_event("event42"));assert(!native_input148_event("event"));
 assert(!native_input148_event("event2/private"));assert(!native_input148_event("mouse0"));
 assert(native_usb148_node("/dev/bus/usb/001/002"));
 assert(!native_usb148_node("/dev/bus/usb/001/002/serial"));
 assert(!native_usb148_node("/dev/bus/usb//002"));
 assert(!native_usb148_node("/dev/bus/usb/001/"));
 native_input148_axes("test","/dev/input/event42");assert(queries==2);assert(closes==1);
 native_usb148_load();assert(probes==3);
 probes=0;timeout_probe=1;native_usb148_load();assert(probes==1);
 probes=0;invalid_clock=1;native_usb148_load();assert(probes==0);
 return 0;
}
'''


class NativeTests(unittest.TestCase):
    def test_real_header(self):
        with tempfile.TemporaryDirectory(prefix='inputusb148-') as folder:
            root = Path(folder)
            (root / 'test.c').write_text(FIXTURE)
            compiled = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function',
                '-I', str(BASE), str(root / 'test.c'), '-o', str(root / 'test')], capture_output=True, text=True, timeout=30)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            result = subprocess.run([str(root / 'test')], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('code=53 min=0 max=2559', result.stdout)
            self.assertNotIn('1234', result.stdout)
            self.assertNotIn('code=54', result.stdout)
            self.assertIn('reason=probe_timeout_or_refusal no_retry=1', result.stdout)

    def test_no_input_reads_or_role_writes(self):
        header = (BASE / 'native-input-usb-148.h').read_text()
        for forbidden in ['EVIOCGRAB', 'read(fd,', 'O_RDWR', 'O_WRONLY', 'mount(', 'chmod(', 'chown(', 'system(']:
            self.assertNotIn(forbidden, header)
        self.assertIn('scanned++ < 128', header)
        self.assertIn('now - last < 20', header)
        self.assertIn('checked++ < 256', header)


if __name__ == '__main__':
    unittest.main()
