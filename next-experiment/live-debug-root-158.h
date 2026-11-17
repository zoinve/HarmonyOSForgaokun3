#ifndef LIVE_DEBUG_ROOT_158_H
#define LIVE_DEBUG_ROOT_158_H
#include <fcntl.h>
#include <linux/openat2.h>
#include <sys/syscall.h>
#include <unistd.h>

/* Resolve absolute target symlinks inside its root, never the caller's root. */
static int live_root158_open(int root, const char *path)
{
    struct open_how how = {
        .flags = O_PATH | O_CLOEXEC,
        .resolve = RESOLVE_IN_ROOT | RESOLVE_NO_MAGICLINKS
    };
    return (int)syscall(SYS_openat2,root,path,&how,sizeof(how));
}
#endif
