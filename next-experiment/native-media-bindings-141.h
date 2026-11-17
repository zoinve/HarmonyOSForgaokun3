#ifndef NATIVE_MEDIA_BINDINGS_141_H
#define NATIVE_MEDIA_BINDINGS_141_H

#include <sys/mount.h>
#include <sys/vfs.h>

static void native_media141_prepare(void)
{
    int saved = errno;
    struct statfs filesystem;
    int present = !statfs("/sys/kernel/debug", &filesystem) &&
                  (unsigned long)filesystem.f_type == 0x64626720UL;
    if (present) {
        dprintf(1, "MEDIA141_DEBUGFS_PRESENT no_remount=1\n");
    } else {
        if (mkdir("/sys/kernel/debug", 0755) && errno != EEXIST) {
            dprintf(1, "MEDIA141_DEBUGFS_REFUSED mkdir_errno=%d\n", errno);
            errno = saved;
            return;
        }
        errno = 0;
        int result = mount("debugfs", "/sys/kernel/debug", "debugfs",
                           MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL);
        dprintf(1, "MEDIA141_DEBUGFS_MOUNT result=%d errno=%d diagnostics_only=1\n", result, errno);
    }
    errno = saved;
}

static void native_media141_observe(const char *stage)
{
    static double last = -1;
    int saved = errno;
    double now = native_media136_now();
    if (now >= 0 && (last < 0 || now - last >= 20)) {
        last = now;
        native_media139_bus(stage, (long long)(now * 1000), "/sys/bus/aprbus/devices");
    }
    errno = saved;
}

#endif
