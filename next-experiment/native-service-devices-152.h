#ifndef NATIVE_SERVICE_DEVICES_152_H
#define NATIVE_SERVICE_DEVICES_152_H

static int native_service152_devnum(const char *path, unsigned *device_major, unsigned *device_minor)
{
    char text[64], extra;
    if (read_text(path, text, sizeof(text))) return 0;
    return sscanf(text, "%u:%u %c", device_major, device_minor, &extra) == 2;
}

static void native_service152_node(const char *stage, const char *pid, const char *name,
                                  int dev, const char *relative, unsigned expected_major, unsigned expected_minor)
{
    struct stat node;
    int result = fstatat(dev, relative, &node, AT_SYMLINK_NOFOLLOW);
    if (result) {
        dprintf(1, "SERVICEDEV152_NODE_MISSING stage=%s pid=%s service=%s node=/dev/%s errno=%d expected_major=%u expected_minor=%u\n",
                stage, pid, name, relative, errno, expected_major, expected_minor);
        return;
    }
    int match = S_ISCHR(node.st_mode) && major(node.st_rdev) == expected_major && minor(node.st_rdev) == expected_minor;
    dprintf(1, "SERVICEDEV152_NODE stage=%s pid=%s service=%s node=/dev/%s uid=%u gid=%u mode=%o char=%d major=%u minor=%u kernel_match=%d\n",
            stage, pid, name, relative, (unsigned)node.st_uid, (unsigned)node.st_gid,
            (unsigned)(node.st_mode & 07777), !!S_ISCHR(node.st_mode), major(node.st_rdev), minor(node.st_rdev), match);
}

static void native_service152_inputs(const char *stage, const char *pid, const char *name, int dev)
{
    DIR *dir = opendir("/sys/class/input");
    if (!dir) return;
    struct dirent *entry;
    unsigned scanned = 0;
    while ((entry = readdir(dir)) && scanned++ < 128) {
        if (!native_input148_event(entry->d_name)) continue;
        char source[512], relative[512];
        snprintf(source, sizeof(source), "/sys/class/input/%s/dev", entry->d_name);
        snprintf(relative, sizeof(relative), "input/%s", entry->d_name);
        unsigned device_major, device_minor;
        if (!native_service152_devnum(source, &device_major, &device_minor)) continue;
        native_service152_node(stage, pid, name, dev, relative, device_major, device_minor);
    }
    closedir(dir);
}

static void native_service152_usb(const char *stage, const char *pid, const char *name, int dev)
{
    DIR *dir = opendir("/sys/bus/usb/devices");
    if (!dir) return;
    struct dirent *entry;
    unsigned scanned = 0;
    while ((entry = readdir(dir)) && scanned++ < 128) {
        if (entry->d_name[0] == '.') continue;
        char source[512], text[64], extra;
        unsigned device_major, device_minor, bus, address;
        snprintf(source, sizeof(source), "/sys/bus/usb/devices/%s/dev", entry->d_name);
        if (!native_service152_devnum(source, &device_major, &device_minor)) continue;
        snprintf(source, sizeof(source), "/sys/bus/usb/devices/%s/busnum", entry->d_name);
        if (read_text(source, text, sizeof(text)) || sscanf(text, "%u %c", &bus, &extra) != 1) continue;
        snprintf(source, sizeof(source), "/sys/bus/usb/devices/%s/devnum", entry->d_name);
        if (read_text(source, text, sizeof(text)) || sscanf(text, "%u %c", &address, &extra) != 1) continue;
        if (device_major != 189 || bus < 1 || bus > 999 || address < 1 || address > 127) continue;
        char relative[64];
        snprintf(relative, sizeof(relative), "bus/usb/%03u/%03u", bus, address);
        native_service152_node(stage, pid, name, dev, relative, device_major, device_minor);
    }
    closedir(dir);
}

static void native_service152_observe(void)
{
    static double last = -1;
    int saved = errno;
    double now = native_media136_now();
    if (!isfinite(now) || now < 0 || (last >= 0 && now - last < 20)) {
        errno = saved;
        return;
    }
    last = now;
    const char *stage = "services_sample152";
    dprintf(1, "SERVICEDEV152_BEGIN stage=%s mono_ms=%lld read_only=1 input_events_read=0\n", stage, (long long)(now * 1000));
    DIR *proc = opendir("/proc");
    if (!proc) {
        dprintf(1, "SERVICEDEV152_REFUSED stage=%s proc_errno=%d\n", stage, errno);
        errno = saved;
        return;
    }
    struct dirent *entry;
    unsigned scanned = 0;
    while ((entry = readdir(proc)) && scanned++ < 1024) {
        if (!entry->d_name[0] || strspn(entry->d_name, "0123456789") != strlen(entry->d_name)) continue;
        char path[512], name[64];
        snprintf(path, sizeof(path), "/proc/%s/comm", entry->d_name);
        if (read_text(path, name, sizeof(name))) continue;
        name[strcspn(name, "\r\n")] = 0;
        if (strcmp(name, "multimodalinput") && strcmp(name, "usb_host") && strcmp(name, "usb_service") &&
            strcmp(name, "hdf_ext_devmgr") && strcmp(name, "storage_daemon") && strcmp(name, "storage_manager")) continue;
        snprintf(path, sizeof(path), "/proc/%s/root/dev", entry->d_name);
        int dev = open(path, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        struct statfs fs;
        struct stat target, outer;
        int error = dev < 0 ? errno : 0;
        if (!error && (fstatfs(dev, &fs) || fstat(dev, &target) || stat("/dev", &outer))) error = errno;
        if (!error && ((unsigned long)fs.f_type != 0x01021994UL || target.st_dev == outer.st_dev)) error = EXDEV;
        if (error) {
            dprintf(1, "SERVICEDEV152_ROOT_REFUSED stage=%s pid=%s service=%s errno=%d\n", stage, entry->d_name, name, error);
            if (dev >= 0) close(dev);
            continue;
        }
        dprintf(1, "SERVICEDEV152_ROOT stage=%s pid=%s service=%s private_tmpfs=1\n", stage, entry->d_name, name);
        native_service152_inputs(stage, entry->d_name, name, dev);
        native_service152_usb(stage, entry->d_name, name, dev);
        close(dev);
    }
    closedir(proc);
    dprintf(1, "SERVICEDEV152_END stage=%s permissions_changed=0 physical_acceptance_not_inferred=1\n", stage);
    errno = saved;
}

#endif
