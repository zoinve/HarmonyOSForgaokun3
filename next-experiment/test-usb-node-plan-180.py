"""Exercise real sysfs fixtures and strict metadata-only block ioctl admission."""
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
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
static int read_text(const char *path,char *text,size_t size) {
 int fd=open(path,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);if(fd<0)return -1;
 ssize_t n=read(fd,text,size-1);close(fd);
 if(n<0 || n>=(ssize_t)size-1)return -1;
 text[n]=0;return 0;
}
#define USB174_NO_OBSERVER
#include "native-usb-storage-174.h"
#define USB175_NO_GUARD
#include "usb-readonly-175.h"
static int step,fail_step,opens,closes,badkind,badsize,badidentity,writable;
static int advance(void){if(++step==fail_step){errno=EIO;return 1;}return 0;}
static int mock_openat(int dir,const char *name,int flags) {
 assert(dir==9);assert(!strcmp(name,opens?"sda1":"sda"));
 assert(flags==(O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC));
 if(advance())return -1;
 return 20+opens++;
}
static int mock_fstat(int fd,struct stat *state) {
 if(advance())return -1;
 memset(state,0,sizeof(*state));state->st_mode=badkind?S_IFREG:S_IFBLK;
 state->st_rdev=makedev(badidentity?259:8,(unsigned)(fd-20));return 0;
}
static int mock_ioctl(int fd,unsigned long request,void *value) {
 assert(request==BLKGETSIZE64 || request==BLKROGET);
 if(advance())return -1;
 if(request==BLKGETSIZE64)*(unsigned long long *)value=(fd==20?61849600ULL:100ULL)*512ULL+(badsize?512:0);
 else *(int *)value=writable?0:1;
 return 0;
}
static int mock_close(int fd){assert(fd==20 || fd==21);++closes;return 0;}
#define openat mock_openat
#define fstat mock_fstat
#define ioctl mock_ioctl
#define close mock_close
#include "usb-node-plan-180.h"
#undef openat
#undef fstat
#undef ioctl
#undef close
static void reset(void){step=fail_step=opens=closes=badkind=badsize=badidentity=writable=0;}
int main(int argc,char **argv) {
 (void)usb174_inventory;(void)usb175_protect;
 if(argc==2){struct usb180_plan plan;memset(&plan,0xff,sizeof(plan));int status=usb180_plan(argv[1],&plan);
  printf("PLAN status=%d count=%u\n",status,plan.count);
  for(unsigned i=0;i<plan.count;++i)printf("NODE name=%s major=%u minor=%u partition=%u sectors=%llu\n",
   plan.nodes[i].name,plan.nodes[i].major,plan.nodes[i].minor,plan.nodes[i].partition,plan.nodes[i].sectors);
  return 0;}
 struct usb180_plan plan={.count=2,.nodes={{.name="sda",.major=8,.minor=0,.sectors=61849600ULL},
  {.name="sda1",.major=8,.minor=1,.partition=1,.sectors=100}}};
 reset();assert(usb180_validate(9,&plan)==0);assert(opens==2 && closes==2);
 for(int i=1;i<=8;++i){reset();fail_step=i;assert(usb180_validate(9,&plan)==-1);assert(closes==opens);}
 reset();badkind=1;assert(usb180_validate(9,&plan)==-1);assert(closes==opens);
 reset();badidentity=1;assert(usb180_validate(9,&plan)==-1);assert(closes==opens);
 reset();badsize=1;assert(usb180_validate(9,&plan)==-1);assert(closes==opens);
 reset();writable=1;assert(usb180_validate(9,&plan)==-1);assert(closes==opens);
 reset();strcpy(plan.nodes[0].name,"../nvme0n1");assert(usb180_validate(9,&plan)==-1);assert(opens==0);
 puts("VALIDATOR_CASES_PASSED metadata_only=1 write_ioctls=0");return 0;
}
'''


class NodePlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='usb-node180-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / 'test.c'
        source.write_text(FIXTURE)
        self.binary = self.root / 'test'
        proc = subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(source),'-o',str(self.binary)],
                              capture_output=True,text=True,timeout=30)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.sys = self.root / 'sys'
        for path in ['class/block','bus/usb','bus/pci']:
            (self.sys / path).mkdir(parents=True)

    def disk(self,name='sda',usb=True,minor=0):
        parent = self.sys / 'devices' / name
        parent.mkdir(parents=True)
        (parent/'subsystem').symlink_to(self.sys/('bus/usb' if usb else 'bus/pci'))
        (parent/'idVendor').write_text('346d\n')
        (parent/'idProduct').write_text('5678\n')
        block=parent/'block'/name
        block.mkdir(parents=True)
        for key,value in dict(removable=1,size=61849600,dev='8:'+str(minor),ro=1).items():
            (block/key).write_text(str(value)+'\n')
        (self.sys/'class/block'/name).symlink_to(block)
        return block

    def partition(self,disk,name='sda1',number=1,minor=1):
        path=disk/name
        path.mkdir()
        for key,value in dict(partition=number,size=100,start=2048,dev='8:'+str(minor),ro=1).items():
            (path/key).write_text(str(value)+'\n')
        (self.sys/'class/block'/name).symlink_to(path)
        return path

    def plan(self):
        proc=subprocess.run([str(self.binary),str(self.sys)],capture_output=True,text=True,timeout=5)
        self.assertEqual(proc.returncode,0,proc.stderr)
        return proc.stdout

    def test_whole_disk_and_real_partition_only(self):
        disk=self.disk()
        self.partition(disk)
        self.disk(name='nvme0n1',usb=False,minor=16)
        text=self.plan()
        self.assertIn('PLAN status=0 count=2',text)
        self.assertNotIn('nvme',text)

    def test_missing_and_ambiguous_refused(self):
        self.assertIn('status=-1 count=0',self.plan())
        self.disk()
        self.disk(name='sdb',minor=16)
        self.assertIn('status=-1 count=0',self.plan())

    def test_writable_partition_or_disk_refused(self):
        disk=self.disk()
        part=self.partition(disk)
        (part/'ro').write_text('0\n')
        self.assertIn('status=-1 count=0',self.plan())
        (part/'ro').write_text('1\n')
        (disk/'ro').write_text('0\n')
        self.assertIn('status=-1 count=0',self.plan())

    def test_duplicate_identity_refused(self):
        self.partition(self.disk(),minor=0)
        self.assertIn('status=-1 count=0',self.plan())

    def test_oversize_partition_refused(self):
        part=self.partition(self.disk())
        (part/'size').write_text('61849601\n')
        self.assertIn('status=-1 count=0',self.plan())

    def test_partition_extent_and_missing_start_refused(self):
        part=self.partition(self.disk())
        (part/'start').write_text('61849599\n')
        self.assertIn('status=-1 count=0',self.plan())
        (part/'start').unlink()
        self.assertIn('status=-1 count=0',self.plan())

    def test_bounded_partition_inventory(self):
        disk=self.disk()
        for number in range(1,33):
            self.partition(disk,name='sda'+str(number),number=number,minor=number)
        self.assertIn('status=-1 count=0',self.plan())

    def test_partition_name_not_parentage(self):
        self.disk()
        foreign=self.disk(name='sda2',usb=False,minor=2)
        (foreign/'partition').write_text('2\n')
        text=self.plan()
        self.assertIn('status=0 count=1',text)
        self.assertNotIn('name=sda2',text)

    def test_all_validator_failures_close_descriptors(self):
        proc=subprocess.run([str(self.binary)],capture_output=True,text=True,timeout=5)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertIn('VALIDATOR_CASES_PASSED',proc.stdout)

    def test_arm64_strict_build_and_execution(self):
        binary=self.root/'test-arm64'
        proc=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',
            '-I',str(BASE),str(self.root/'test.c'),'-o',str(binary)],capture_output=True,text=True,timeout=60)
        self.assertEqual(proc.returncode,0,proc.stderr)
        proc=subprocess.run(['qemu-aarch64',str(binary)],capture_output=True,text=True,timeout=10)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.partition(self.disk())
        proc=subprocess.run(['qemu-aarch64',str(binary),str(self.sys)],capture_output=True,text=True,timeout=10)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertIn('PLAN status=0 count=2',proc.stdout)


if __name__ == '__main__':
    unittest.main()
