"""Planner cases, actual outer compilation, and isolated real-mount verification."""
from pathlib import Path
import hashlib
import os
import runpy
import subprocess
import tempfile
import unittest

BASE = Path(__file__).resolve().parent
PARENT = Path('/home/zoinve/harmony-virgl-883/commercial61-native-164')
HEADERS = Path('/home/zoinve/harmony-virgl-883/commercial61-native-168')
TRANSFORM = runpy.run_path(str(BASE / 'persistent-lifecycle-172.py'))['outer172']
HARNESS = r'''
#define _GNU_SOURCE
#include <assert.h>
#include <fcntl.h>
#include <sched.h>
#include <signal.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <sys/wait.h>
#include <unistd.h>
#include "persistent-unmount-plan-172.h"
static struct persistent172_mount rows[PERSISTENT172_MAX_MOUNTS];
static int plan(const char *text,unsigned *count) {
 FILE *f=fmemopen((void *)text,strlen(text),"r");assert(f);
 int result=persistent172_plan(f,rows,count,7,3);fclose(f);return result;
}
int main(int argc,char **argv) {
 unsigned count=0;
 if(argc==1) {
  const char *tree="1 0 0:1 / / rw - tmpfs tmpfs rw\n"
   "2 1 7:3 / /data rw - ext4 /dev/loop3 rw\n"
   "3 1 7:3 /files /mnt/alias rw - ext4 /dev/loop3 rw\n"
   "4 3 0:22 / /mnt/alias/nested rw - tmpfs tmpfs rw\n"
   "5 2 0:23 / /data/a\\040b rw - tmpfs tmpfs rw\n"
   "6 1 7:0 / /system ro - ext4 /dev/loop0 ro\n";
  assert(!plan(tree,&count) && count==6);
  assert(!strcmp(rows[4].path,"/data/a b"));
  unsigned removed=0;int next;
  while((next=persistent172_next(rows,count))>=0) {
   assert(rows[next].id!=1 && rows[next].id!=6);
   if(rows[next].id==2)assert(rows[4].removed);
   if(rows[next].id==3)assert(rows[3].removed);
   rows[next].removed=1;++removed;
  }
  assert(next==-1 && removed==4);
  assert(plan("1 0 7:3 / / rw - ext4 /dev/loop3 rw\n",&count));
  assert(plan("1 0 0:1 / / rw - tmpfs tmpfs rw\n2 1 7:3 / /data rw - ext4 loop rw\n3 1 0:2 / /data rw - tmpfs tmpfs rw\n",&count));
  assert(plan("1 0 0:1 / /bad\\999 rw - tmpfs tmpfs rw\n",&count));
  assert(plan("1 0 0:1 / / rw - tmpfs tmpfs rw\n1 0 0:2 / /x rw - tmpfs tmpfs rw\n",&count));
  assert(plan("invalid\n",&count));
  assert(!plan("1 2 7:3 / /data rw - ext4 loop rw\n2 1 7:3 / /alias rw - ext4 loop rw\n",&count));
  assert(persistent172_next(rows,count)==-2);
  puts("planner cases passed");return 0;
 }
 assert(argc==2 && geteuid()==0);
 char data[4096],alias[4096],nested[4096],protected[4096];
 assert(snprintf(data,sizeof(data),"%s/data",argv[1])<(int)sizeof(data));
 assert(snprintf(alias,sizeof(alias),"%s/alias",argv[1])<(int)sizeof(alias));
 assert(snprintf(nested,sizeof(nested),"%s/alias/nested",argv[1])<(int)sizeof(nested));
 assert(snprintf(protected,sizeof(protected),"%s/protected",argv[1])<(int)sizeof(protected));
 assert(!mkdir(data,0700) && !mkdir(alias,0700) && !mkdir(protected,0700));
 assert(!mount("tmpfs",data,"tmpfs",MS_NODEV|MS_NOSUID,"size=1m"));
 assert(!mount(data,alias,NULL,MS_BIND,NULL));
 assert(!mkdir(nested,0700));
 assert(!mount("tmpfs",nested,"tmpfs",MS_NODEV|MS_NOSUID,"size=1m"));
 assert(!mount("tmpfs",protected,"tmpfs",MS_NODEV|MS_NOSUID,"size=1m"));
 struct stat st,keep,after;assert(!stat(data,&st) && !stat(protected,&keep));
 int procdir=open("/proc/self",O_RDONLY|O_DIRECTORY|O_CLOEXEC);assert(procdir>=0);
 int pinned=getenv("HARMONY172_PINNED_MOUNTS")!=NULL;
 if(pinned) {
  int ready[2];assert(!pipe(ready));pid_t child=fork();assert(child>=0);
  if(!child) {
   close(ready[0]);assert(!unshare(CLONE_NEWNS));
   assert(!chdir(argv[1]) && !chroot(".") && !chdir("/"));
   assert(write(ready[1],"1",1)==1);close(ready[1]);for(;;)pause();
  }
  close(ready[1]);char status;assert(read(ready[0],&status,1)==1);close(ready[0]);
  char path[128];snprintf(path,sizeof(path),"/proc/%d/ns/mnt",child);
  int ns=open(path,O_RDONLY|O_CLOEXEC);assert(ns>=0);
  snprintf(path,sizeof(path),"/proc/%d/root",child);
  int root=open(path,O_RDONLY|O_DIRECTORY|O_CLOEXEC);assert(root>=0);
  assert(!kill(child,SIGKILL));int state;assert(waitpid(child,&state,0)==child && WIFSIGNALED(state));
  assert(!setns(ns,CLONE_NEWNS) && !fchdir(root) && !chroot(".") && !chdir("/"));
  close(ns);close(root);
  strcpy(data,"/data");strcpy(alias,"/alias");strcpy(nested,"/alias/nested");strcpy(protected,"/protected");
 }
 int info=openat(procdir,"mountinfo",O_RDONLY|O_CLOEXEC);assert(info>=0);
 FILE *f=fdopen(info,"r");assert(f);
 assert(!persistent172_plan(f,rows,&count,major(st.st_dev),minor(st.st_dev)));fclose(f);
 unsigned removed=0;int next;
 while((next=persistent172_next(rows,count))>=0) {
  if(pinned)assert(!strcmp(rows[next].path,data) || !strcmp(rows[next].path,alias) || !strcmp(rows[next].path,nested));
  else assert(!strncmp(rows[next].path,argv[1],strlen(argv[1])) && rows[next].path[strlen(argv[1])]=='/');
  assert(strcmp(rows[next].path,protected));
  assert(!umount(rows[next].path));rows[next].removed=1;++removed;
 }
 assert(next==-1 && removed==3);
 info=openat(procdir,"mountinfo",O_RDONLY|O_CLOEXEC);assert(info>=0);f=fdopen(info,"r");assert(f);
 assert(!persistent172_plan(f,rows,&count,major(st.st_dev),minor(st.st_dev)));fclose(f);
 assert(persistent172_next(rows,count)==-1);
 assert(!stat(protected,&after) && after.st_dev==keep.st_dev);
 assert(!umount(protected));
 close(procdir);
 puts(pinned ? "reaped target namespace entered; proc descriptor remains usable after chroot; data aliases removed" :
  "real alias and nested mounts removed; unrelated mount preserved");return 0;
}
'''

class LifecycleTests(unittest.TestCase):
    def test_mount_planner_and_optional_real_mounts(self):
        with tempfile.TemporaryDirectory(prefix='harmony-lifecycle172-') as directory:
            root = Path(directory)
            source, binary = root / 'test.c', root / 'test'
            source.write_text(HARNESS)
            subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(source),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)
            if os.environ.get('HARMONY172_REAL_MOUNTS') == '1':
                self.assertEqual(os.geteuid(),0)
                subprocess.run(['unshare','--mount','--propagation','private',str(binary),str(root)],check=True)
                with tempfile.TemporaryDirectory(prefix='harmony-pinned172-') as pinned:
                    env = dict(os.environ,HARMONY172_PINNED_MOUNTS='1')
                    subprocess.run(['unshare','--mount','--propagation','private',str(binary),pinned],check=True,env=env)

    def test_full_outer_compile_and_reap_order(self):
        source = TRANSFORM((PARENT / 'init.c').read_text(),'0'*64,'eaa446cb-b02a-494f-8a5e-a02c8516cbc7')
        stop = source.index('            native_live159_stop();')
        pin = source.index('            persistent172_pin(child);')
        kill = source.index('                kill(child,SIGKILL);',pin)
        reaped = source.index('            persistent172_reaped(child,got);')
        finish = source.index('    persistent172_finish();')
        self.assertTrue(stop < pin < kill < reaped < finish)
        self.assertNotIn('    persistent166_finish();',source)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'init.c'
            path.write_text(source)
            for compiler in ['gcc','aarch64-linux-gnu-gcc']:
                args = [compiler,'-O2','-Wall','-Wextra','-Werror','-I',str(BASE),'-I',str(HEADERS),str(path)]
                if compiler == 'gcc':
                    args += ['-c','-o',str(Path(directory) / 'init-host.o')]
                else:
                    args += ['-static',str(BASE / 'baremetal-diagnostic-core.c'),'-o',str(Path(directory) / 'init-arm64')]
                proc = subprocess.run(args,capture_output=True,text=True)
                self.assertEqual(proc.returncode,0,proc.stderr)
                if compiler == 'aarch64-linux-gnu-gcc':
                    binary = Path(directory) / 'init-arm64'
                    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
                    subprocess.run(args,check=True,capture_output=True)
                    self.assertEqual(hashlib.sha256(binary.read_bytes()).hexdigest(),digest)
                    guard = subprocess.run(['qemu-aarch64',str(binary)],capture_output=True,text=True,timeout=10)
                    self.assertEqual(guard.returncode,77,guard.stderr)
                    self.assertEqual(guard.stderr,'Diagnostic entry requires PID 1\n')
            print('host object, reproducible ARM64 static link, and PID1 refusal verified',flush=True)

    def test_no_detach_or_runtime_reset_fallback(self):
        text = (BASE / 'persistent-data-172.h').read_text()
        for forbidden in ['MNT_DETACH','MNT_FORCE','ftruncate(', 'unlink(', 'system(', 'chmod(']:
            self.assertNotIn(forbidden,text)
        self.assertIn('got == target',text)
        self.assertIn('remaining_data_mounts=0',text)
        self.assertIn('original_services_graceful_shutdown=0',text)

if __name__ == '__main__':
    unittest.main()
