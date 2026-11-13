#define _GNU_SOURCE
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

/* Disposable namespace only: no target services, SELinux or GPU operations. */
int main(int argc,char **argv)
{
    char root[]="/var/tmp/native-root-regression-003-XXXXXX";
    if(!mkdtemp(root))return 90;
    pid_t child=fork();if(child<0)return 91;
    if(!child){
        if(unshare(CLONE_NEWNS) || mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL))_exit(92);
        int ns=open("/proc/self/ns/mnt",O_RDONLY|O_CLOEXEC);if(ns<0)_exit(93);
        if(mount("tmpfs",root,"tmpfs",MS_NOSUID|MS_NODEV,"size=1m"))_exit(94);
        if(argc>1 && !strcmp(argv[1],"namespace")){
            /* Linux OPEN_TREE_NAMESPACE: create a namespace rooted at target. */
            int rooted=(int)syscall(SYS_open_tree,AT_FDCWD,root,2|O_CLOEXEC|AT_RECURSIVE);
            if(rooted<0 || setns(rooted,CLONE_NEWNS)){
                perror("rooted mount namespace");_exit(95);
            }
            close(ns);ns=rooted;
        }else if(argc>1){
            if(chdir(root) || mkdir(".old-root",0700) || syscall(SYS_pivot_root,".",".old-root") ||
               chdir("/") || umount2("/.old-root",MNT_DETACH) || rmdir("/.old-root")){
                perror("pivot namespace root");_exit(96);
            }
        }else if(chdir(root) || chroot(".") || chdir("/"))_exit(97);
        struct stat before,after;
        if(stat("/",&before) || setns(ns,CLONE_NEWNS) || stat("/",&after))_exit(98);
        int same=before.st_dev==after.st_dev && before.st_ino==after.st_ino;
        dprintf(1,"ROOT_NAMESPACE_REGRESSION pivot=%d stable=%d before=%llu:%llu after=%llu:%llu\n",
            argc>1,same,(unsigned long long)before.st_dev,(unsigned long long)before.st_ino,
            (unsigned long long)after.st_dev,(unsigned long long)after.st_ino);
        _exit(same?0:1);
    }
    int status;if(waitpid(child,&status,0)!=child)return 99;
    if(rmdir(root))return 100;
    return WIFEXITED(status)?WEXITSTATUS(status):101;
}
