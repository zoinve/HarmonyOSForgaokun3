#ifndef NATIVE_MEDIA_136_H
#define NATIVE_MEDIA_136_H

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <time.h>
#include <unistd.h>

static const char *const native_media136_modules[] = {
    "qrtr_smd", "qcom_glink_smem", "qcom_pd_mapper", "apr",
    "snd_soc_lpass_va_macro", "snd_soc_lpass_rx_macro",
    "snd_soc_lpass_tx_macro", "snd_soc_lpass_wsa_macro", "soundwire_qcom",
    "snd_soc_wcd938x_sdw", "snd_soc_wcd938x", "snd_soc_wsa883x",
    "q6prm_clocks", "q6apm_dai", "q6apm_lpass_dais", "snd_soc_sc8280xp",
    "hci_uart", "qcom_q6v5_pas"
};

static int native_media136_allowed(double start, double now, unsigned requested)
{
    return isfinite(start) && isfinite(now) && start >= 0 && now >= start &&
           requested > 0 && requested <= 30 && now - start <= 30 - requested;
}

static double native_media136_now(void)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) return -1;
    return now.tv_sec + now.tv_nsec / 1e9;
}

static void native_media136_load(void)
{
    double start = native_media136_now();
    dprintf(1, "MEDIA136_LOAD_BEGIN admission_seconds=30 per_probe_seconds=4 hardware_success_not_inferred=1\n");
    for (size_t i = 0; i < sizeof(native_media136_modules) / sizeof(native_media136_modules[0]); ++i) {
        const char *module = native_media136_modules[i];
        if (!native_media136_allowed(start, native_media136_now(), 4)) {
            dprintf(1, "MEDIA136_LOAD_STOP module=%s reason=group_budget no_retry=1\n", module);
            break;
        }
        char path[256];
        snprintf(path, sizeof(path), "/sys/module/%s", module);
        if (!access(path, F_OK)) {
            dprintf(1, "MEDIA136_MODULE_PRESENT module=%s binding_not_inferred=1\n", module);
            continue;
        }
        char *args[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", (char *)module, NULL};
        int result = probe(module, args, 4);
        dprintf(1, "MEDIA136_MODULE_RESULT module=%s status=%d binding_not_inferred=1\n", module, result);
        if (result == 124 || result == 125) {
            dprintf(1, "MEDIA136_LOAD_STOP module=%s reason=probe_timeout_or_refusal no_retry=1\n", module);
            break;
        }
    }
    dprintf(1, "MEDIA136_LOAD_END hardware_success_not_inferred=1\n");
}

static void native_media136_stream(const char *stage, const char *path, unsigned limit)
{
    int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    int error = fd < 0 ? errno : 0;
    unsigned total = 0, interrupted = 0;
    int eof = 0;
    dprintf(1, "MEDIA136_FILE_BEGIN stage=%s path=%s limit=%u\n", stage, path, limit);
    while (fd >= 0 && total < limit) {
        char buffer[1024];
        unsigned wanted = limit - total;
        if (wanted > sizeof(buffer)) wanted = sizeof(buffer);
        ssize_t count = read(fd, buffer, wanted);
        if (count < 0 && errno == EINTR && ++interrupted < 4) continue;
        if (count < 0) { error = errno; break; }
        if (!count) { eof = 1; break; }
        interrupted = 0;
        if (dprintf(1, "%.*s", (int)count, buffer) < 0) { error = errno; break; }
        total += (unsigned)count;
    }
    if (fd >= 0) close(fd);
    dprintf(1, "\nMEDIA136_FILE_END stage=%s path=%s bytes=%u eof=%d errno=%d\n",
            stage, path, total, eof, error);
}

static void native_media136_class(const char *stage, long long mono_ms,
                                  const char *root, const char *prefix,
                                  const char *const *attributes, size_t count)
{
    DIR *dir = opendir(root);
    if (!dir) {
        dprintf(1, "MEDIA136_CLASS_MISSING stage=%s path=%s errno=%d\n", stage, root, errno);
        return;
    }
    unsigned scanned = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) && scanned++ < 128) {
        if (strncmp(entry->d_name, prefix, strlen(prefix))) continue;
        const char *suffix = entry->d_name + strlen(prefix);
        if (!*suffix || strspn(suffix, "0123456789") != strlen(suffix)) continue;
        char path[512];
        int length = snprintf(path, sizeof(path), "%s/%s", root, entry->d_name);
        if (length < 0 || (size_t)length >= sizeof(path)) continue;
        dprintf(1, "MEDIA136_CLASS_ENTRY stage=%s path=%s controller_ready_not_inferred=1\n", stage, path);
        native_driver133_directory(stage, mono_ms, path, attributes, count);
    }
    closedir(dir);
}

static void native_media136_nodes(const char *stage)
{
    DIR *dir = opendir("/dev/snd");
    if (!dir) {
        dprintf(1, "MEDIA136_SOUND_NODES_MISSING stage=%s errno=%d\n", stage, errno);
        return;
    }
    struct dirent *entry;
    unsigned scanned = 0;
    while ((entry = readdir(dir)) && scanned++ < 128) {
        struct stat node;
        if (fstatat(dirfd(dir), entry->d_name, &node, AT_SYMLINK_NOFOLLOW) || !S_ISCHR(node.st_mode)) continue;
        dprintf(1, "MEDIA136_SOUND_NODE stage=%s name=%s uid=%u gid=%u mode=%o major=%u minor=%u\n",
                stage, entry->d_name, (unsigned)node.st_uid, (unsigned)node.st_gid,
                (unsigned)(node.st_mode & 07777), major(node.st_rdev), minor(node.st_rdev));
    }
    closedir(dir);
}

static void native_media136_observe(const char *stage)
{
    int saved = errno;
    double now = native_media136_now();
    if (now < 0) {
        dprintf(1, "MEDIA136_OBSERVE_REFUSED stage=%s clock_errno=%d\n", stage, errno);
        errno = saved;
        return;
    }
    long long mono_ms = (long long)(now * 1000);
    dprintf(1, "MEDIA136_OBSERVE_BEGIN stage=%s mono_ms=%lld read_only=1\n", stage, mono_ms);
    native_media136_stream(stage, "/proc/asound/cards", 8192);
    native_media136_stream(stage, "/proc/asound/pcm", 8192);
    native_media136_nodes(stage);
    const char *remote[] = {"name", "state", "firmware"};
    const char *hci[] = {"type"};
    native_media136_class(stage, mono_ms, "/sys/class/remoteproc", "remoteproc", remote, 3);
    native_media136_class(stage, mono_ms, "/sys/class/bluetooth", "hci", hci, 1);
    const char *state[] = {"initstate"};
    for (size_t i = 0; i < sizeof(native_media136_modules) / sizeof(native_media136_modules[0]); ++i) {
        char path[256];
        snprintf(path, sizeof(path), "/sys/module/%s", native_media136_modules[i]);
        native_driver133_directory(stage, mono_ms, path, state, 1);
    }
    dprintf(1, "MEDIA136_OBSERVE_END stage=%s hdi_playback_pairing_not_inferred=1\n", stage);
    errno = saved;
}

#endif
