"""Verify that namespace metadata is read-only and kernel identities are compared."""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
FIXTURE = runpy.run_path(str(BASE / 'test-native-input-usb-148.py'))['FIXTURE'].split('int main(void) {', 1)[0]
FIXTURE = FIXTURE.replace('#include <sys/stat.h>', '#include <sys/stat.h>\n#include <sys/vfs.h>')
FIXTURE = FIXTURE.replace('static int read_text(const char *p,char *b,size_t n) { (void)p;(void)b;(void)n;return -1; }',
    'static const char *test_text;\nstatic int read_text(const char *p,char *b,size_t n) { (void)p;if(!test_text)return -1;snprintf(b,n,"%s",test_text);return 0; }')
FIXTURE += r'''
static int missing;
static int mock_fstatat(int fd,const char *path,struct stat *s,int flags) {
 assert(fd==99);assert(flags==AT_SYMLINK_NOFOLLOW);assert(!strcmp(path,"bus/usb/005/002"));
 if(missing){errno=ENOENT;return -1;}
 memset(s,0,sizeof(*s));s->st_mode=S_IFCHR|0660;s->st_rdev=makedev(189,513);s->st_uid=3023;s->st_gid=3023;return 0;
}
#define fstatat mock_fstatat
#include "native-service-devices-152.h"
int main(void) {
 unsigned a=0,b=0;
 test_text="189:513\n";assert(native_service152_devnum("/test",&a,&b));assert(a==189&&b==513);
 test_text="189:513 extra";assert(!native_service152_devnum("/test",&a,&b));
 test_text=NULL;assert(!native_service152_devnum("/test",&a,&b));
 native_service152_node("test","42","usb_host",99,"bus/usb/005/002",189,513);
 native_service152_node("test","42","usb_host",99,"bus/usb/005/002",189,514);
 missing=1;native_service152_node("test","42","usb_host",99,"bus/usb/005/002",189,513);
 return 0;
}
'''


class NamespaceTests(unittest.TestCase):
    def test_actual_header(self):
        with tempfile.TemporaryDirectory(prefix='servicedev152-') as folder:
            root = Path(folder)
            (root / 'test.c').write_text(FIXTURE)
            compiled = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function',
                '-I', str(BASE), str(root / 'test.c'), '-o', str(root / 'test')], capture_output=True, text=True, timeout=30)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            proc = subprocess.run([str(root / 'test')], capture_output=True, text=True, timeout=5)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('kernel_match=1', proc.stdout)
            self.assertIn('kernel_match=0', proc.stdout)
            self.assertIn('NODE_MISSING', proc.stdout)
            self.assertIn('uid=3023 gid=3023 mode=660', proc.stdout)

    def test_readonly_bounded_private_dev_guard(self):
        text = (BASE / 'native-service-devices-152.h').read_text()
        for forbidden in ['O_WRONLY', 'O_RDWR', 'mknod(', 'mount(', 'fchmod(', 'fchown(', 'setuid(', 'ioctl(']:
            self.assertNotIn(forbidden, text)
        self.assertIn('target.st_dev == outer.st_dev', text)
        self.assertIn('0x01021994UL', text)
        self.assertIn('now - last < 20', text)
        self.assertIn('scanned++ < 1024', text)


if __name__ == '__main__':
    unittest.main()
