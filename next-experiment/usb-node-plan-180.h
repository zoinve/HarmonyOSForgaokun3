#ifndef USB_NODE_PLAN_180_H
#define USB_NODE_PLAN_180_H

#include <linux/fs.h>

#define USB180_MAX_NODES 32
struct usb180_node {
    char name[256];
    unsigned major, minor, partition;
    unsigned long long sectors, start;
};
struct usb180_plan {
    unsigned count;
    struct usb180_node nodes[USB180_MAX_NODES];
};

/* Select metadata only. This function neither opens media nor creates nodes. */
static int usb180_plan(const char *sysroot, struct usb180_plan *plan)
{
    struct usb180_plan pending = {0};
    char disk[256] = {0}, base[PATH_MAX], path[PATH_MAX + 320], selected[PATH_MAX];
    unsigned disk_major = 0, disk_minor = 0;
    memset(plan, 0, sizeof(*plan));
    if (usb175_select(sysroot, disk, &disk_major, &disk_minor) != 1) return -1;
    if (snprintf(base, sizeof(base), "%s/class/block", sysroot) >= (int)sizeof(base)) return -1;
    snprintf(path, sizeof(path), "%s/%s", base, disk);
    if (!realpath(path, selected)) return -1;
    DIR *dir = opendir(base);
    if (!dir) return -1;
    unsigned scanned = 0, whole = 0;
    struct dirent *entry;
    int failed = 0;
    while ((entry = readdir(dir))) {
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;
        if (++scanned > 256) { failed = 1; break; }
        const char *name = entry->d_name;
        if (strspn(name, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.") != strlen(name)) continue;
        char resolved[PATH_MAX];
        snprintf(path, sizeof(path), "%s/%s", base, name);
        if (!realpath(path, resolved)) { failed = 1; break; }
        int is_disk = !strcmp(resolved, selected);
        char *slash = strrchr(resolved, '/');
        if (!is_disk && (!slash || (size_t)(slash - resolved) != strlen(selected) ||
                        strncmp(resolved, selected, strlen(selected)))) continue;
        if (pending.count == USB180_MAX_NODES) { failed = 1; break; }
        struct usb180_node *node = &pending.nodes[pending.count];
        unsigned long long ro = 0, partition = 0;
        snprintf(path, sizeof(path), "%s/%s/ro", base, name);
        if (!usb174_number(path, &ro) || ro != 1) { failed = 1; break; }
        snprintf(path, sizeof(path), "%s/%s/size", base, name);
        if (!usb174_number(path, &node->sectors) || !node->sectors ||
            node->sectors > USB175_SECTORS) { failed = 1; break; }
        snprintf(path, sizeof(path), "%s/%s/partition", base, name);
        if (!is_disk && (!usb174_number(path, &partition) || !partition || partition > 128)) { failed = 1; break; }
        if (!is_disk) {
            snprintf(path, sizeof(path), "%s/%s/start", base, name);
            if (!usb174_number(path, &node->start) || !node->start ||
                node->start >= USB175_SECTORS || node->sectors > USB175_SECTORS - node->start) {
                failed = 1; break;
            }
        }
        char text[64], extra;
        snprintf(path, sizeof(path), "%s/%s/dev", base, name);
        if (read_text(path, text, sizeof(text)) ||
            sscanf(text, "%u:%u %c", &node->major, &node->minor, &extra) != 2 ||
            !node->major || node->major > 4095 || node->minor > 1048575) { failed = 1; break; }
        if (is_disk && (node->major != disk_major || node->minor != disk_minor ||
                        node->sectors != USB175_SECTORS)) { failed = 1; break; }
        for (unsigned i = 0; i < pending.count; ++i) {
            struct usb180_node *other = &pending.nodes[i];
            if ((other->major == node->major && other->minor == node->minor) ||
                other->partition == partition) failed = 1;
        }
        if (failed) break;
        strcpy(node->name, name);
        node->partition = (unsigned)partition;
        ++pending.count;
        whole += (unsigned)is_disk;
    }
    closedir(dir);
    if (failed || whole != 1) return -1;
    *plan = pending;
    return 0;
}

/* Revalidate each real node using metadata ioctls, without reading media bytes. */
static int usb180_validate(int devdir, const struct usb180_plan *plan)
{
    if (!plan->count || plan->count > USB180_MAX_NODES) return -1;
    for (unsigned i = 0; i < plan->count; ++i) {
        const struct usb180_node *node = &plan->nodes[i];
        if (!node->name[0] || node->name[0] == '.' ||
            strspn(node->name, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-") != strlen(node->name) ||
            !node->sectors || node->sectors > USB175_SECTORS) return -1;
        int fd = openat(devdir, node->name, O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
        if (fd < 0) return -1;
        struct stat state;
        unsigned long long bytes = 0;
        int ro = -1;
        int failed = fstat(fd, &state) || !S_ISBLK(state.st_mode) ||
            major(state.st_rdev) != node->major || minor(state.st_rdev) != node->minor ||
            ioctl(fd, BLKGETSIZE64, &bytes) || bytes != node->sectors * 512ULL ||
            ioctl(fd, BLKROGET, &ro) || ro != 1;
        close(fd);
        if (failed) return -1;
    }
    return 0;
}

#endif
