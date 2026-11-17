#ifndef NATIVE_MEDIA_BINDINGS_139_H
#define NATIVE_MEDIA_BINDINGS_139_H

static void native_media139_bus(const char *stage, long long mono_ms, const char *root)
{
    DIR *dir = opendir(root);
    if (!dir) {
        dprintf(1, "MEDIA139_BUS_MISSING stage=%s path=%s errno=%d\n", stage, root, errno);
        return;
    }
    struct dirent *entry;
    unsigned scanned = 0;
    while ((entry = readdir(dir)) && scanned++ < 128) {
        if (entry->d_name[0] == '.') continue;
        char path[512], link[544], target[512];
        int length = snprintf(path, sizeof(path), "%s/%s", root, entry->d_name);
        if (length < 0 || (size_t)length >= sizeof(path)) continue;
        length = snprintf(link, sizeof(link), "%s/driver", path);
        if (length < 0 || (size_t)length >= sizeof(link)) continue;
        ssize_t bytes = readlink(link, target, sizeof(target) - 1);
        int error = bytes < 0 ? errno : 0;
        if (bytes >= (ssize_t)sizeof(target) - 1) {
            dprintf(1, "MEDIA139_DRIVER_REFUSED stage=%s path=%s reason=truncated_link\n", stage, path);
            continue;
        }
        if (bytes >= 0) target[bytes] = 0;
        const char *driver = bytes < 0 ? "absent" : strrchr(target, '/');
        if (bytes >= 0) driver = driver ? driver + 1 : target;
        dprintf(1, "MEDIA139_BINDING stage=%s path=%s driver=%s errno=%d\n", stage, path, driver, error);
        const char *attributes[] = {"modalias"};
        native_driver133_directory(stage, mono_ms, path, attributes, 1);
    }
    closedir(dir);
}

static void native_media139_observe(const char *stage)
{
    static double last = -1;
    int saved = errno;
    double now = native_media136_now();
    if (now < 0 || (last >= 0 && now - last < 20)) {
        errno = saved;
        return;
    }
    last = now;
    long long mono_ms = (long long)(now * 1000);
    dprintf(1, "MEDIA139_BINDINGS_BEGIN stage=%s mono_ms=%lld read_only=1\n", stage, mono_ms);
    native_media136_stream(stage, "/sys/kernel/debug/devices_deferred", 16384);
    native_media139_bus(stage, mono_ms, "/sys/bus/soundwire/devices");
    native_media139_bus(stage, mono_ms, "/sys/bus/apr/devices");
    native_media139_bus(stage, mono_ms, "/sys/bus/gpr/devices");
    native_media139_bus(stage, mono_ms, "/sys/bus/rpmsg/devices");
    const char *sound[] = {"modalias"};
    native_driver133_directory(stage, mono_ms, "/sys/bus/platform/devices/sound", sound, 1);
    dprintf(1, "MEDIA139_BINDINGS_END stage=%s hdi_acceptance_not_inferred=1\n", stage);
    errno = saved;
}

#endif
