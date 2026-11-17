"""Test USB-only selection and every preflight/ioctl failure without a disk."""
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
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <linux/fs.h>
static int read_text(const char *path,char *text,size_t capacity) {
 int fd=open(path,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(fd<0)return -1;
 ssize_t n=read(fd,text,capacity-1);close(fd);
 if(n<0 || n>=(ssize_t)capacity-1)return -1;
 text[n]=0;return 0;
}
#define USB174_NO_OBSERVER
#include "native-usb-storage-174.h"
static int step,fail_step,protected_flag,sets,closes,wrong_size,wrong_device;
static int advance(void){return ++step==fail_step;}
static int mock_open(const char *path,int flags) {
 assert(!strcmp(path,"/dev/sda"));
 assert(flags==(O_RDONLY|O_NOFOLLOW|O_CLOEXEC));return advance()?-1:17;
}
static int mock_stat(int fd,struct stat *state) {
 assert(fd==17);if(advance())return -1;
 memset(state,0,sizeof(*state));state->st_mode=S_IFBLK|0600;
 state->st_rdev=makedev(wrong_device?259:8,0);return 0;
}
static int mock_ioctl(int fd,unsigned long request,void *arg) {
 assert(fd==17);if(advance())return -1;
 if(request==BLKGETSIZE64)*(unsigned long long *)arg=61849600ULL*512ULL+(wrong_size?512:0);
 else if(request==BLKROGET)*(int *)arg=protected_flag;
 else {assert(request==BLKROSET);assert(*(int *)arg==1);protected_flag=1;++sets;}
 return 0;
}
static int mock_close(int fd){assert(fd==17);++closes;return 0;}
#define open mock_open
#define fstat mock_stat
#define ioctl mock_ioctl
#define close mock_close
#define USB175_NO_GUARD
#include "usb-readonly-175.h"
#undef open
#undef fstat
#undef ioctl
#undef close
static void reset(void){step=fail_step=protected_flag=sets=closes=wrong_size=wrong_device=0;}
int main(int argc,char **argv) {
 (void)usb174_inventory;
 if(argc==2){char name[256];unsigned maj=0,min=0;int n=usb175_select(argv[1],name,&maj,&min);
  printf("SELECT result=%d",n);if(n==1)printf(" name=%s major=%u minor=%u",name,maj,min);puts("");return 0;}
 reset();assert(usb175_protect("sda",8,0)==0);assert(sets==1 && protected_flag==1 && closes==1);
 reset();protected_flag=1;assert(usb175_protect("sda",8,0)==0);assert(sets==0 && closes==1);
 for(int i=1;i<=6;++i){reset();fail_step=i;assert(usb175_protect("sda",8,0)==1);assert(closes==(i!=1));}
 reset();wrong_size=1;assert(usb175_protect("sda",8,0)==1);assert(sets==0);
 reset();wrong_device=1;assert(usb175_protect("sda",8,0)==1);assert(sets==0);
 reset();assert(usb175_protect("../nvme0n1",8,0)==1);assert(step==0);
 return 0;
}
'''


class ReadonlyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='usb-readonly175-')
        self.root = Path(self.temp.name)
        source = self.root / 'test.c'
        source.write_text(FIXTURE)
        self.binary = self.root / 'test'
        result = subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE),
                                 str(source), '-o', str(self.binary)], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.sys = self.root / 'sys'
        (self.sys / 'class/block').mkdir(parents=True)
        (self.sys / 'bus/usb').mkdir(parents=True)
        (self.sys / 'bus/pci').mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def add_disk(self, name, usb=True):
        parent = self.sys / 'devices' / name
        parent.mkdir(parents=True)
        (parent / 'subsystem').symlink_to(self.sys / ('bus/usb' if usb else 'bus/pci'))
        for attr, value in {'idVendor':'346d', 'idProduct':'5678', 'removable':'1',
                            'size':'61849600', 'dev':'8:0'}.items():
            (parent / attr).write_text(value + '\n')
        (self.sys / 'class/block' / name).symlink_to(parent)
        return parent

    def selection(self):
        return subprocess.check_output([str(self.binary), str(self.sys)], text=True, timeout=5)

    def test_ioctl_success_already_protected_and_all_failures(self):
        result = subprocess.run([str(self.binary)], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count('USB175_PROTECTED'), 2)
        self.assertEqual(result.stdout.count('USB175_REFUSED'), 8)

    def test_never_select_internal_disk_even_with_same_ids(self):
        self.add_disk('nvme0n1', usb=False)
        self.assertIn('result=0', self.selection())
        self.add_disk('sda')
        self.assertIn('result=1 name=sda major=8 minor=0', self.selection())

    def test_ambiguity_partition_wrong_capacity_and_nonremovable_refused(self):
        first = self.add_disk('sda')
        for attr, value in [('size','1'), ('removable','0'), ('partition','1')]:
            original = (first / attr).read_text() if (first / attr).exists() else None
            (first / attr).write_text(value + '\n')
            self.assertIn('result=0', self.selection())
            if original is None: (first / attr).unlink()
            else: (first / attr).write_text(original)
        self.add_disk('sdb')
        self.assertIn('result=-1', self.selection())


if __name__ == '__main__':
    unittest.main()
