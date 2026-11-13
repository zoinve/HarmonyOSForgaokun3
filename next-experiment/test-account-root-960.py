"""Real Linux regression: root discovery must survive loss of absolute /proc."""
from pathlib import Path
import subprocess
import sys
import tempfile

source=Path(sys.argv[1]).read_text()
if 'static int enter_account_root(' in source:
    resolver=source[source.index('static int enter_account_root('):source.index('/* A bounded caller')]
else:
    resolver='static int enter_account_root(int fd) { (void)fd; return chdir("/proc/1/root") || chroot(".") || chdir("/"); }'
test=r'''
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
RESOLVER
int main(void) {
    char empty[]="/tmp/account-root-test-XXXXXX";
    if (!mkdtemp(empty)) return 10;
    char proc[]="/tmp/account-proc-test-XXXXXX";
    if (!mkdtemp(proc) || mount("proc",proc,"proc",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)) return 17;
    int fd=open(proc, O_PATH|O_DIRECTORY);
    if (fd<0) return 11;
    if (umount2(proc,MNT_DETACH) || rmdir(proc)) return 18;
    pid_t child=fork();
    if (!child) {
        if (chroot(empty) || chdir("/")) _exit(12);
        if (!access("/proc",F_OK)) _exit(13);
        if (enter_account_root(fd)) { perror("root discovery"); _exit(14); }
        _exit(access("/proc/1/status",R_OK) ? 15 : 0);
    }
    int status;
    if (child<0 || waitpid(child,&status,0)<0) return 16;
    close(fd); rmdir(empty);
    if (status) { fprintf(stderr,"root discovery regression status=%d\n",status); return 1; }
    puts("PASS: pinned proc descriptor resolves PID1 root without absolute /proc");
    return 0;
}
'''.replace('RESOLVER',resolver)
with tempfile.TemporaryDirectory(prefix='account-root-test-') as tmp:
    c=Path(tmp)/'test.c';exe=Path(tmp)/'test';c.write_text(test)
    subprocess.run(['gcc','-O2','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
