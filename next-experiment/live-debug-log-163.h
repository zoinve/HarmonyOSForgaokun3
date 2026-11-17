#ifndef LIVE_DEBUG_LOG_163_H
#define LIVE_DEBUG_LOG_163_H
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <linux/openat2.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#ifndef LIVE163_HILOG_PREFIX
#define LIVE163_HILOG_PREFIX "/mnt/lab/"
#endif
#ifndef LIVE163_NATIVE_PATH
#define LIVE163_NATIVE_PATH "/run/diagnostic.log"
#endif

static int live_log163_refuse(unsigned item,unsigned stage,int error)
{
    if (!error) error=EIO;
    dprintf(1,"LIVE163_LOG_REFUSED item=%u stage=%u errno=%d\n",item,stage,error);
    errno=error;
    return -1;
}

static int live_log163_path(const char *path,unsigned item)
{
    if (item==2) return !strcmp(path,LIVE163_NATIVE_PATH);
    if (item!=1 || strncmp(path,LIVE163_HILOG_PREFIX,strlen(LIVE163_HILOG_PREFIX)) ||
        strstr(path,"/../") || strstr(path,"/./")) return 0;
    const char *last=strrchr(path,'/');
    return last && !strcmp(last+1,"interactive-hilog030.log");
}

/* Reopen in this mount namespace, then prove it is the original captured inode. */
static int live_log163_reopen(int inherited,unsigned item)
{
    struct stat original,current;
    if (fstat(inherited,&original)) return live_log163_refuse(item,1,errno);
    if (!S_ISREG(original.st_mode)) return live_log163_refuse(item,2,EINVAL);
    char reference[64],path[PATH_MAX];
    snprintf(reference,sizeof(reference),"/proc/self/fd/%d",inherited);
    ssize_t length=readlink(reference,path,sizeof(path)-1);
    if (length<0) return live_log163_refuse(item,3,errno);
    if (!length || length>=(ssize_t)sizeof(path)-1) return live_log163_refuse(item,4,ENAMETOOLONG);
    path[length]=0;
    if (!live_log163_path(path,item)) return live_log163_refuse(item,5,EINVAL);
    int root=open("/",O_PATH | O_DIRECTORY | O_CLOEXEC);
    if (root<0) return live_log163_refuse(item,6,errno);
    struct open_how how={.flags=O_RDONLY | O_CLOEXEC,
        .resolve=RESOLVE_IN_ROOT | RESOLVE_NO_MAGICLINKS | RESOLVE_NO_SYMLINKS};
    int fd=(int)syscall(SYS_openat2,root,path,&how,sizeof(how));
    int error=errno;
    close(root);
    if (fd<0) return live_log163_refuse(item,7,error);
    if (fstat(fd,&current)) {
        error=errno;close(fd);return live_log163_refuse(item,8,error);
    }
    if (!S_ISREG(current.st_mode) || original.st_dev!=current.st_dev || original.st_ino!=current.st_ino) {
        close(fd);return live_log163_refuse(item,9,ESTALE);
    }
    dprintf(1,"LIVE163_LOG_READY item=%u source_reopened_in_current_mount_namespace=1 original_inode_verified=1\n",item);
    return fd;
}
#endif
