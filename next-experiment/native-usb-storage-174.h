#ifndef NATIVE_USB_STORAGE_174_H
#define NATIVE_USB_STORAGE_174_H

#include <limits.h>

static int usb174_number(const char *path, unsigned long long *value)
{
    char text[64], *end;
    if (read_text(path, text, sizeof(text)) || text[0] < '0' || text[0] > '9') return 0;
    errno = 0;
    unsigned long long number = strtoull(text, &end, 10);
    if (errno || (*end && strcmp(end, "\n"))) return 0;
    *value = number;
    return 1;
}

static int usb174_hex(const char *path, unsigned *value)
{
    char text[32], extra;
    if (read_text(path, text, sizeof(text))) return 0;
    text[strcspn(text, "\r\n")] = 0;
    return strlen(text) == 4 && strspn(text, "0123456789abcdefABCDEF") == 4 &&
           sscanf(text, "%x %c", value, &extra) == 1;
}

/* Require an actual USB subsystem ancestor, not a name containing "usb". */
static int usb174_parent(const char *sysroot, const char *device, unsigned *vid, unsigned *pid)
{
    char current[PATH_MAX], link[PATH_MAX + 32], subsystem[PATH_MAX], expected[PATH_MAX];
    if (!realpath(device, current) || snprintf(expected, sizeof(expected), "%s/bus/usb", sysroot) >= (int)sizeof(expected)) return 0;
    size_t prefix = strlen(sysroot);
    if (strncmp(current, sysroot, prefix) || current[prefix] != '/') return 0;
    for (unsigned depth = 0; depth < 32; ++depth) {
        snprintf(link, sizeof(link), "%s/subsystem", current);
        if (realpath(link, subsystem) && !strcmp(subsystem, expected)) {
            snprintf(link, sizeof(link), "%s/idVendor", current);
            if (!usb174_hex(link, vid)) goto parent;
            snprintf(link, sizeof(link), "%s/idProduct", current);
            if (usb174_hex(link, pid)) return 1;
        }
parent:
        {
            char *slash = strrchr(current, '/');
            if (!slash || (size_t)(slash - current) <= prefix) break;
            *slash = 0;
        }
    }
    return 0;
}

static unsigned usb174_nodes(int dir, dev_t expected, unsigned depth, unsigned *budget)
{
    if (dir < 0 || depth > 4 || !*budget) return 0;
    int copy = openat(dir, ".", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (copy < 0) return 0;
    DIR *entries = fdopendir(copy);
    if (!entries) { close(copy); return 0; }
    struct dirent *entry;
    unsigned matches = 0;
    while (*budget && (entry = readdir(entries))) {
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;
        --*budget;
        struct stat state;
        if (fstatat(dir, entry->d_name, &state, AT_SYMLINK_NOFOLLOW)) continue;
        if (S_ISBLK(state.st_mode) && state.st_rdev == expected) ++matches;
        if (S_ISDIR(state.st_mode)) {
            int child = openat(dir, entry->d_name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
            if (child >= 0) { matches += usb174_nodes(child, expected, depth + 1, budget); close(child); }
        }
    }
    closedir(entries);
    return matches;
}

static unsigned usb174_inventory(const char *sysroot, int target_dev)
{
    char base[PATH_MAX], path[PATH_MAX + 320], text[64], extra;
    if (snprintf(base, sizeof(base), "%s/class/block", sysroot) >= (int)sizeof(base)) return 0;
    DIR *dir = opendir(base);
    if (!dir) { dprintf(1, "USBSTORAGE174_REFUSED reason=block_class_unavailable errno=%d\n", errno); return 0; }
    struct dirent *entry;
    unsigned scanned = 0, count = 0;
    while ((entry = readdir(dir)) && scanned++ < 256) {
        const char *name = entry->d_name;
        if (!name[0] || name[0] == '.' || strspn(name, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.") != strlen(name)) continue;
        snprintf(path, sizeof(path), "%s/%s", base, name);
        unsigned vid, pid, maj, min;
        if (!usb174_parent(sysroot, path, &vid, &pid)) continue;
        snprintf(path, sizeof(path), "%s/%s/dev", base, name);
        if (read_text(path, text, sizeof(text)) || sscanf(text, "%u:%u %c", &maj, &min, &extra) != 2 ||
            !maj || maj > 4095 || min > 1048575) continue;
        unsigned long long sectors, readonly, removable, partition;
        snprintf(path, sizeof(path), "%s/%s/size", base, name);
        if (!usb174_number(path, &sectors)) continue;
        snprintf(path, sizeof(path), "%s/%s/ro", base, name);
        int ro_valid = usb174_number(path, &readonly) && readonly <= 1;
        snprintf(path, sizeof(path), "%s/%s/removable", base, name);
        int removable_valid = usb174_number(path, &removable) && removable <= 1;
        snprintf(path, sizeof(path), "%s/%s/partition", base, name);
        int part_valid = usb174_number(path, &partition) && partition <= 1048575;
        unsigned budget = 1024;
        unsigned nodes = usb174_nodes(target_dev, makedev(maj, min), 0, &budget);
        dprintf(1, "USBSTORAGE174_BLOCK name=%s vid=%04x pid=%04x major=%u minor=%u sectors=%llu ro=%d removable=%d partition=%lld target_dev_available=%d matching_target_nodes=%u node_scan_complete=%d\n",
                name, vid, pid, maj, min, sectors, ro_valid ? (int)readonly : -1,
                removable_valid ? (int)removable : -1, part_valid ? (long long)partition : -1,
                target_dev >= 0, nodes, target_dev >= 0 && budget > 0);
        ++count;
    }
    dprintf(1, "USBSTORAGE174_INVENTORY count=%u entry_limit_reached=%d raw_blocks_opened=0 serials_read=0\n", count, scanned >= 256);
    closedir(dir);
    return count;
}

#ifndef USB174_NO_OBSERVER
static void native_usb_storage174_observe(pid_t target)
{
    static double last = -1;
    double now = native_media136_now();
    int saved = errno;
    if (!isfinite(now) || now < 0 || (last >= 0 && now - last < 10)) return;
    last = now;
    dprintf(1, "USBSTORAGE174_BEGIN target=%d mono_ms=%lld read_only=1 service_acceptance_not_inferred=1\n", target, (long long)(now * 1000));
    char path[128];
    snprintf(path, sizeof(path), "/proc/%d/root/dev", target);
    int dev = open(path, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    (void)usb174_inventory("/sys", dev);
    if (dev >= 0) close(dev);
    const char *helpers[] = {"mount.ntfs", "fsck.ntfs", "blkid"};
    for (unsigned i = 0; i < 3; ++i) {
        snprintf(path, sizeof(path), "/proc/%d/root/system/bin/%s", target, helpers[i]);
        struct stat state;
        int present = !stat(path, &state) && S_ISREG(state.st_mode) && (state.st_mode & 0111);
        dprintf(1, "USBSTORAGE174_HELPER name=%s executable_file_present=%d executed=0\n", helpers[i], present);
    }
    struct stat state;
    snprintf(path, sizeof(path), "/proc/%d/root/dev/fuse", target);
    int fuse = !lstat(path, &state) && S_ISCHR(state.st_mode) && major(state.st_rdev) == 10 && minor(state.st_rdev) == 229;
    dprintf(1, "USBSTORAGE174_FUSE target_node_present=%d\n", fuse);
    dprintf(1, "USBSTORAGE174_END raw_blocks_opened=0 nodes_created=0 media_written=0\n");
    errno = saved;
}
#endif

#endif
