#ifndef USB_READONLY_176_H
#define USB_READONLY_176_H

#include <linux/fs.h>

/* Trace only the guard's fixed metadata operations, never device contents. */
static int usb176_guard_open(const char *path, int flags)
{
    int fd = open(path, flags), saved = errno;
    dprintf(1, "USB176_STEP stage=open status=%d errno=%d\n", fd < 0 ? -1 : 0, fd < 0 ? saved : 0);
    errno = saved;
    return fd;
}

static int usb176_guard_fstat(int fd, struct stat *state)
{
    int status = fstat(fd, state), saved = errno;
    dprintf(1, "USB176_STEP stage=fstat status=%d errno=%d block=%d major=%u minor=%u\n",
            status, status ? saved : 0, !status && S_ISBLK(state->st_mode),
            status ? 0 : major(state->st_rdev), status ? 0 : minor(state->st_rdev));
    errno = saved;
    return status;
}

static int usb176_guard_ioctl(int fd, unsigned long request, void *argument)
{
    const char *stage = request == BLKGETSIZE64 ? "get_size" : request == BLKROGET ? "get_ro" :
                        request == BLKROSET ? "set_ro" : NULL;
    if (!stage || !argument || (request == BLKROSET && *(int *)argument != 1)) {
        dprintf(1, "USB176_STEP stage=ioctl_refused status=-1 errno=%d\n", EINVAL);
        errno = EINVAL;
        return -1;
    }
    int status = ioctl(fd, request, argument), saved = errno;
    unsigned long long value = status ? 0 : request == BLKGETSIZE64 ?
        *(unsigned long long *)argument : (unsigned long long)*(int *)argument;
    dprintf(1, "USB176_STEP stage=%s status=%d errno=%d value_valid=%d value=%llu\n",
            stage, status, status ? saved : 0, status == 0, value);
    errno = saved;
    return status;
}

#pragma push_macro("open")
#pragma push_macro("fstat")
#pragma push_macro("ioctl")
#undef open
#undef fstat
#undef ioctl
#define open usb176_guard_open
#define fstat usb176_guard_fstat
#define ioctl usb176_guard_ioctl
#include "usb-readonly-175.h"
#pragma pop_macro("ioctl")
#pragma pop_macro("fstat")
#pragma pop_macro("open")

#endif
