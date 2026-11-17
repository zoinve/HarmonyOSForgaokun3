#ifndef NATIVE_INPUT_USB_148_H
#define NATIVE_INPUT_USB_148_H

#include <linux/input.h>
#include <sys/ioctl.h>

static const char *const native_usb148_modules[] = {"usb_storage", "uas", "exfat"};

static void native_usb148_load(void)
{
    double start = native_media136_now();
    dprintf(1, "INPUTUSB148_LOAD_BEGIN group_seconds=12 per_probe_seconds=4\n");
    for (size_t i = 0; i < sizeof(native_usb148_modules) / sizeof(native_usb148_modules[0]); ++i) {
        const char *module = native_usb148_modules[i];
        double now = native_media136_now();
        if (!isfinite(start) || !isfinite(now) || start < 0 || now < start || now - start > 8) {
            dprintf(1, "INPUTUSB148_LOAD_STOP module=%s reason=budget_or_clock no_retry=1\n", module);
            break;
        }
        char path[256];
        snprintf(path, sizeof(path), "/sys/module/%s", module);
        if (!access(path, F_OK)) {
            dprintf(1, "INPUTUSB148_MODULE_PRESENT module=%s storage_acceptance_not_inferred=1\n", module);
            continue;
        }
        char *args[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", (char *)module, NULL};
        int result = probe(module, args, 4);
        dprintf(1, "INPUTUSB148_MODULE_RESULT module=%s status=%d storage_acceptance_not_inferred=1\n", module, result);
        if (result == 124 || result == 125) {
            dprintf(1, "INPUTUSB148_LOAD_STOP module=%s reason=probe_timeout_or_refusal no_retry=1\n", module);
            break;
        }
    }
    dprintf(1, "INPUTUSB148_LOAD_END storage_acceptance_not_inferred=1\n");
}

static int native_input148_event(const char *name)
{
    return !strncmp(name, "event", 5) && name[5] && strspn(name + 5, "0123456789") == strlen(name + 5);
}

static void native_input148_axes(const char *stage, const char *node)
{
    struct stat state;
    int fd = open(node, O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC);
    int error = fd < 0 ? errno : 0;
    if (!error && fstat(fd, &state)) error = errno;
    if (!error && !S_ISCHR(state.st_mode)) error = ENODEV;
    if (error) {
        dprintf(1, "INPUTUSB148_EVDEV_REFUSED stage=%s node=%s errno=%d\n", stage, node, error);
    } else {
        dprintf(1, "INPUTUSB148_EVDEV_NODE stage=%s node=%s uid=%u gid=%u mode=%o major=%u minor=%u\n",
                stage, node, (unsigned)state.st_uid, (unsigned)state.st_gid,
                (unsigned)(state.st_mode & 07777), major(state.st_rdev), minor(state.st_rdev));
        unsigned char bits[(ABS_MAX + 8) / 8] = {0};
        if (ioctl(fd, EVIOCGBIT(EV_ABS, sizeof(bits)), bits) < 0) {
            dprintf(1, "INPUTUSB148_CAPS_FAILED stage=%s node=%s errno=%d\n", stage, node, errno);
        } else {
            const unsigned codes[] = {ABS_X, ABS_Y, ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TRACKING_ID};
            for (size_t i = 0; i < sizeof(codes) / sizeof(codes[0]); ++i) {
                unsigned code = codes[i];
                if (!(bits[code / 8] & (1U << (code % 8)))) continue;
                struct input_absinfo axis;
                if (ioctl(fd, EVIOCGABS(code), &axis) < 0) {
                    dprintf(1, "INPUTUSB148_AXIS_FAILED stage=%s node=%s code=%u errno=%d\n", stage, node, code, errno);
                    continue;
                }
                dprintf(1, "INPUTUSB148_AXIS stage=%s node=%s code=%u min=%d max=%d fuzz=%d flat=%d resolution=%d\n",
                        stage, node, code, axis.minimum, axis.maximum, axis.fuzz, axis.flat, axis.resolution);
            }
        }
    }
    if (fd >= 0) close(fd);
}

static void native_input148_devices(const char *stage, long long mono_ms)
{
    DIR *dir = opendir("/sys/class/input");
    if (!dir) {
        dprintf(1, "INPUTUSB148_INPUT_MISSING stage=%s errno=%d\n", stage, errno);
        return;
    }
    struct dirent *entry;
    unsigned scanned = 0;
    const char *attrs[] = {"name", "id/bustype", "id/vendor", "id/product", "properties", "capabilities/ev", "capabilities/abs", "capabilities/rel"};
    while ((entry = readdir(dir)) && scanned++ < 128) {
        if (!native_input148_event(entry->d_name)) continue;
        char path[512], node[512];
        snprintf(path, sizeof(path), "/sys/class/input/%s/device", entry->d_name);
        snprintf(node, sizeof(node), "/dev/input/%s", entry->d_name);
        native_driver133_directory(stage, mono_ms, path, attrs, sizeof(attrs) / sizeof(attrs[0]));
        native_input148_axes(stage, node);
    }
    closedir(dir);
}

static int native_usb148_node(const char *node)
{
    const char *prefix = "/dev/bus/usb/";
    if (strncmp(node, prefix, strlen(prefix))) return 0;
    const char *bus = node + strlen(prefix), *slash = strchr(bus, '/');
    return slash && slash != bus && strspn(bus, "0123456789") == (size_t)(slash - bus) &&
           slash[1] && strspn(slash + 1, "0123456789") == strlen(slash + 1);
}

static void native_usb148_devices(const char *stage, long long mono_ms)
{
    const char *root = "/sys/bus/usb/devices";
    DIR *dir = opendir(root);
    if (!dir) {
        dprintf(1, "INPUTUSB148_USB_MISSING stage=%s errno=%d\n", stage, errno);
        return;
    }
    struct dirent *entry;
    unsigned scanned = 0;
    const char *attrs[] = {"idVendor", "idProduct", "bDeviceClass", "bInterfaceClass", "bInterfaceSubClass", "bInterfaceProtocol", "speed", "authorized", "busnum", "devnum"};
    while ((entry = readdir(dir)) && scanned++ < 128) {
        if (entry->d_name[0] == '.') continue;
        char path[512], driver_path[544], target[512];
        snprintf(path, sizeof(path), "%s/%s", root, entry->d_name);
        snprintf(driver_path, sizeof(driver_path), "%s/driver", path);
        ssize_t length = readlink(driver_path, target, sizeof(target) - 1);
        int error = length < 0 ? errno : 0;
        if (length >= (ssize_t)sizeof(target) - 1) continue;
        if (length >= 0) target[length] = 0;
        const char *driver = length < 0 ? "absent" : strrchr(target, '/');
        if (length >= 0) driver = driver ? driver + 1 : target;
        dprintf(1, "INPUTUSB148_USB_BINDING stage=%s path=%s driver=%s errno=%d\n", stage, path, driver, error);
        native_driver133_directory(stage, mono_ms, path, attrs, sizeof(attrs) / sizeof(attrs[0]));
        char bus_path[544], address_path[544], bus[16], address[16], node[128];
        snprintf(bus_path, sizeof(bus_path), "%s/busnum", path);
        snprintf(address_path, sizeof(address_path), "%s/devnum", path);
        if (read_text(bus_path, bus, sizeof(bus)) || read_text(address_path, address, sizeof(address))) continue;
        bus[strcspn(bus, "\r\n")] = 0;
        address[strcspn(address, "\r\n")] = 0;
        if (!bus[0] || strspn(bus, "0123456789") != strlen(bus) || !address[0] || strspn(address, "0123456789") != strlen(address)) continue;
        long b = strtol(bus, NULL, 10), a = strtol(address, NULL, 10);
        if (b < 1 || b > 999 || a < 1 || a > 999) continue;
        snprintf(node, sizeof(node), "/dev/bus/usb/%03ld/%03ld", b, a);
        struct stat state;
        if (lstat(node, &state) || !S_ISCHR(state.st_mode)) {
            dprintf(1, "INPUTUSB148_USB_NODE_MISSING stage=%s node=%s\n", stage, node);
            continue;
        }
        dprintf(1, "INPUTUSB148_USB_NODE stage=%s node=%s uid=%u gid=%u mode=%o\n",
                stage, node, (unsigned)state.st_uid, (unsigned)state.st_gid, (unsigned)(state.st_mode & 07777));
    }
    closedir(dir);
}

static void native_input148_service_fds(const char *stage)
{
    DIR *proc = opendir("/proc");
    if (!proc) return;
    struct dirent *entry;
    unsigned scanned = 0;
    while ((entry = readdir(proc)) && scanned++ < 1024) {
        if (!entry->d_name[0] || strspn(entry->d_name, "0123456789") != strlen(entry->d_name)) continue;
        char path[512], comm[64];
        snprintf(path, sizeof(path), "/proc/%s/comm", entry->d_name);
        if (read_text(path, comm, sizeof(comm))) continue;
        comm[strcspn(comm, "\r\n")] = 0;
        if (strcmp(comm, "multimodalinput") && strcmp(comm, "usb_host") && strcmp(comm, "usb_service") &&
            strcmp(comm, "hdf_ext_devmgr") && strcmp(comm, "storage_daemon") && strcmp(comm, "storage_manager")) continue;
        dprintf(1, "INPUTUSB148_SERVICE stage=%s pid=%s name=%s\n", stage, entry->d_name, comm);
        snprintf(path, sizeof(path), "/proc/%s/fd", entry->d_name);
        DIR *fds = opendir(path);
        if (!fds) {
            dprintf(1, "INPUTUSB148_FDS_REFUSED stage=%s pid=%s errno=%d\n", stage, entry->d_name, errno);
            continue;
        }
        struct dirent *fd;
        unsigned checked = 0;
        while ((fd = readdir(fds)) && checked++ < 256) {
            if (fd->d_name[0] == '.') continue;
            char target[512];
            ssize_t count = readlinkat(dirfd(fds), fd->d_name, target, sizeof(target) - 1);
            if (count < 0 || count >= (ssize_t)sizeof(target) - 1) continue;
            target[count] = 0;
            if ((!strncmp(target, "/dev/input/", 11) && native_input148_event(target + 11)) || native_usb148_node(target))
                dprintf(1, "INPUTUSB148_SERVICE_FD stage=%s pid=%s name=%s fd=%s node=%s\n", stage, entry->d_name, comm, fd->d_name, target);
        }
        closedir(fds);
    }
    closedir(proc);
}

static void native_input148_observe(const char *stage)
{
    static double last = -1;
    int saved = errno;
    double now = native_media136_now();
    if (!isfinite(now) || now < 0 || (last >= 0 && now - last < 20)) {
        errno = saved;
        return;
    }
    last = now;
    long long mono_ms = (long long)(now * 1000);
    dprintf(1, "INPUTUSB148_OBSERVE_BEGIN stage=%s mono_ms=%lld read_only=1 input_events_read=0\n", stage, mono_ms);
    native_input148_devices(stage, mono_ms);
    native_usb148_devices(stage, mono_ms);
    native_input148_service_fds(stage);
    const char *attrs[] = {"initstate"};
    for (size_t i = 0; i < sizeof(native_usb148_modules) / sizeof(native_usb148_modules[0]); ++i) {
        char path[256];
        snprintf(path, sizeof(path), "/sys/module/%s", native_usb148_modules[i]);
        native_driver133_directory(stage, mono_ms, path, attrs, 1);
    }
    dprintf(1, "INPUTUSB148_OBSERVE_END stage=%s physical_interaction_acceptance_not_inferred=1\n", stage);
    errno = saved;
}

#endif
