#ifndef NATIVE_DRIVER_OBSERVER_133_H
#define NATIVE_DRIVER_OBSERVER_133_H

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/vfs.h>
#include <time.h>
#include <unistd.h>

static void native_driver133_attribute(const char *stage, long long mono_ms,
                                       const char *path, int dir, const char *attribute)
{
    char value[128];
    int fd = openat(dir, attribute, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    int error = fd < 0 ? errno : 0;
    size_t used = 0;
    while (!error && used < sizeof(value) - 1) {
        ssize_t count = read(fd, value + used, sizeof(value) - 1 - used);
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) { error = errno; break; }
        if (!count) break;
        used += (size_t)count;
        if (used == sizeof(value) - 1) error = EOVERFLOW;
    }
    if (fd >= 0) close(fd);
    if (!error && (!used || memchr(value, 0, used))) error = ENODATA;
    while (used && (value[used - 1] == '\n' || value[used - 1] == '\r')) --used;
    if (!error && (!used || memchr(value, '\n', used) || memchr(value, '\r', used))) error = ENODATA;
    value[used] = 0;
    if (error)
        dprintf(1, "GAOKUN_DRIVER133 stage=%s mono_ms=%lld path=%s attr=%s valid=0 errno=%d\n",
                stage, mono_ms, path, attribute, error);
    else
        dprintf(1, "GAOKUN_DRIVER133 stage=%s mono_ms=%lld path=%s attr=%s valid=1 value=%s\n",
                stage, mono_ms, path, attribute, value);
}

static void native_driver133_directory(const char *stage, long long mono_ms,
                                       const char *path, const char *const *attributes, size_t count)
{
    int dir = open(path, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    struct statfs fs;
    int error = dir < 0 ? errno : 0;
    if (!error && fstatfs(dir, &fs)) error = errno;
    if (!error && fs.f_type != 0x62656572) error = ENODEV;
    if (error)
        dprintf(1, "GAOKUN_DRIVER133_REFUSED stage=%s path=%s errno=%d\n", stage, path, error);
    else
        for (size_t i = 0; i < count; ++i)
            native_driver133_attribute(stage, mono_ms, path, dir, attributes[i]);
    if (dir >= 0) close(dir);
}

static void native_driver_observer133(const char *stage)
{
    int saved = errno;
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) {
        dprintf(1, "GAOKUN_DRIVER133_REFUSED stage=%s clock_errno=%d\n", stage, errno);
        errno = saved;
        return;
    }
    long long mono_ms = (long long)now.tv_sec * 1000 + now.tv_nsec / 1000000;
    const char *backlight[] = {"brightness", "actual_brightness", "max_brightness"};
    const char *battery[] = {"type", "present", "capacity", "status", "voltage_now", "current_now", "temp", "health"};
    const char *adapter[] = {"type", "online"};
    native_driver133_directory(stage, mono_ms, "/sys/class/backlight/ae96000.dsi.0", backlight, 3);
    native_driver133_directory(stage, mono_ms, "/sys/class/power_supply/battery", battery, 8);
    native_driver133_directory(stage, mono_ms, "/sys/class/power_supply/gaokun-ec-adapter", adapter, 2);
    errno = saved;
}

#endif
