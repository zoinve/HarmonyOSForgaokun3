#ifndef USB_READONLY_175_H
#define USB_READONLY_175_H

#include <linux/fs.h>

#define USB175_SECTORS 61849600ULL

static int usb175_select(const char *sysroot, char name[256], unsigned *device_major, unsigned *device_minor)
{
    char base[PATH_MAX], path[PATH_MAX + 320], text[64], extra;
    if (snprintf(base, sizeof(base), "%s/class/block", sysroot) >= (int)sizeof(base)) return -1;
    DIR *dir = opendir(base);
    if (!dir) return -1;
    unsigned scanned = 0, matches = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) && scanned++ < 256) {
        const char *candidate = entry->d_name;
        if (!candidate[0] || candidate[0] == '.' || strlen(candidate) > 255 ||
            strspn(candidate, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.") != strlen(candidate)) continue;
        unsigned vid, pid, maj, min;
        snprintf(path, sizeof(path), "%s/%s", base, candidate);
        if (!usb174_parent(sysroot, path, &vid, &pid) || vid != 0x346d || pid != 0x5678) continue;
        snprintf(path, sizeof(path), "%s/%s/partition", base, candidate);
        struct stat state;
        if (!stat(path, &state) || errno != ENOENT) continue;
        unsigned long long removable, sectors;
        snprintf(path, sizeof(path), "%s/%s/removable", base, candidate);
        if (!usb174_number(path, &removable) || removable != 1) continue;
        snprintf(path, sizeof(path), "%s/%s/size", base, candidate);
        if (!usb174_number(path, &sectors) || sectors != USB175_SECTORS) continue;
        snprintf(path, sizeof(path), "%s/%s/dev", base, candidate);
        if (read_text(path, text, sizeof(text)) || sscanf(text, "%u:%u %c", &maj, &min, &extra) != 2 ||
            !maj || maj > 4095 || min > 1048575) continue;
        ++matches;
        strcpy(name, candidate);
        *device_major = maj;
        *device_minor = min;
    }
    closedir(dir);
    if (scanned >= 256 || matches > 1) return -1;
    return matches == 1;
}

/* BLKROSET changes only the kernel's write-protection flag; no media writes. */
static int usb175_protect(const char *name, unsigned device_major, unsigned device_minor)
{
    char path[288];
    if (!name[0] || strspn(name, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.") != strlen(name) || name[0] == '.') return 1;
    if (snprintf(path, sizeof(path), "/dev/%s", name) >= (int)sizeof(path)) return 1;
    int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    struct stat state;
    unsigned long long bytes = 0;
    int before = -1, after = -1, one = 1;
    int error = fd < 0;
    if (!error && (fstat(fd, &state) || !S_ISBLK(state.st_mode) ||
        major(state.st_rdev) != device_major || minor(state.st_rdev) != device_minor)) error = 1;
    if (!error && (ioctl(fd, BLKGETSIZE64, &bytes) || bytes != USB175_SECTORS * 512ULL)) error = 1;
    if (!error && (ioctl(fd, BLKROGET, &before) || (before != 0 && before != 1))) error = 1;
    if (!error && !before && ioctl(fd, BLKROSET, &one)) error = 1;
    if (!error && (ioctl(fd, BLKROGET, &after) || after != 1)) error = 1;
    if (fd >= 0) close(fd);
    if (error) {
        dprintf(1, "USB175_REFUSED reason=identity_size_or_readonly_guard\n");
        return 1;
    }
    dprintf(1, "USB175_PROTECTED name=%s vid=346d pid=5678 major=%u minor=%u bytes=%llu before=%d after=1 kernel_flag_only=1 media_data_writes=0\n",
            name, device_major, device_minor, bytes, before);
    return 0;
}

#ifndef USB175_NO_GUARD
static int native_usb_storage175_guard(void)
{
    char command[8192];
    const char *optin = " harmony.usb_readonly175=1";
    if (read_text("/proc/cmdline", command, sizeof(command))) return 1;
    const char *found = strstr(command, optin);
    if (!found || (found[strlen(optin)] && found[strlen(optin)] != ' ' && found[strlen(optin)] != '\n')) {
        dprintf(1, "USB175_REFUSED reason=explicit_readonly_optin_required\n");
        return 1;
    }
    for (unsigned attempt = 0; attempt < 11; ++attempt) {
        char name[256] = {0};
        unsigned maj = 0, min = 0;
        int selected = usb175_select("/sys", name, &maj, &min);
        if (selected < 0) break;
        if (selected == 1) return usb175_protect(name, maj, min);
        if (attempt < 10) sleep(1);
    }
    dprintf(1, "USB175_REFUSED reason=expected_unique_usb_disk_not_found\n");
    return 1;
}
#endif

#endif
