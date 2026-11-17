#ifndef NATIVE_BACKLIGHT_PERMISSIONS_130_H
#define NATIVE_BACKLIGHT_PERMISSIONS_130_H

#include <sys/vfs.h>

static int native_backlight_permissions130(void)
{
    const char *directory = "/sys/class/backlight/ae96000.dsi.0";
    int dir = open(directory, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (dir < 0) return -1;
    struct statfs fs;
    int result = -1;
    int fd = -1;
    struct stat before, after;
    if (fstatfs(dir, &fs) || fs.f_type != 0x62656572) goto done;
    fd = openat(dir, "brightness", O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0 || fstat(fd, &before) || !S_ISREG(before.st_mode)) goto done;
    /* Only the original composer group may write this board-owned attribute. */
    if (fchown(fd, 0, 3036) || fchmod(fd, 0660) || fstat(fd, &after)) goto done;
    if (after.st_uid || after.st_gid != 3036 || (after.st_mode & 0777) != 0660) goto done;
    dprintf(1, "GAOKUN_BACKLIGHT130_PERMISSION before_uid=%u before_gid=%u before_mode=%o uid=0 gid=3036 mode=660 sysfs_verified=1 brightness_written=0\n",
            before.st_uid, before.st_gid, before.st_mode & 0777);
    result = 0;
done:
    if (fd >= 0) close(fd);
    close(dir);
    return result;
}

#endif
