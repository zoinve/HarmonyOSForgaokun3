/* Offline diagnostic candidate only. No HarmonyOS launch or host installation. */
#define _GNU_SOURCE
#include "baremetal-diagnostic-core.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <unistd.h>

static int ram = -1, run = -1, mounted;
static unsigned snapshot_id;

static int read_text(const char *path, char *data, size_t size)
{
    int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, data, size - 1);
    close(fd);
    if (n < 0 || (size_t)n >= size - 1) return -1;
    data[n] = 0;
    return 0;
}

static void hold(void)
{
    for (;;) pause(); /* No guard refusal may fall through into diagnostics. */
}

static void snapshot(void)
{
    if (run < 0 || ram < 0) return;
    char name[40], buffer[4096];
    snprintf(name, sizeof(name), "phase-%03u.log", ++snapshot_id);
    int fd = openat(run, name, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (fd < 0) { dprintf(2, "SNAPSHOT_OPEN_FAILED errno=%d\n", errno); return; }
    off_t offset = 0;
    ssize_t n;
    int failed = 0;
    while ((n = pread(ram, buffer, sizeof(buffer), offset)) > 0) {
        ssize_t written = 0;
        while (written < n) {
            ssize_t w = write(fd, buffer + written, (size_t)(n - written));
            if (w < 0 && errno == EINTR) continue;
            if (w <= 0) { failed = 1; break; }
            written += w;
        }
        if (failed) break;
        offset += n;
    }
    if (n < 0 || fsync(fd) || fsync(run)) failed = 1;
    close(fd);
    dprintf(2, "SNAPSHOT name=%s failed=%d\n", name, failed);
}

static int probe(const char *name, char *const argv[], unsigned timeout)
{
    dprintf(1, "PHASE_BEGIN %s\n", name);
    snapshot();
    int status = diag_run(argv, timeout);
    dprintf(1, "PHASE_END %s status=%d\n", name, status);
    snapshot();
    return status;
}

static int identify(const char *device, char *output, size_t size)
{
    int fd = open("/run/blkid-export", O_RDWR | O_CREAT | O_TRUNC | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (fd < 0) return -1;
    int saved = dup(1);
    if (saved < 0 || dup2(fd, 1) < 0) { close(fd); return -1; }
    char *argv[] = {"/sbin/blkid", "-p", "-o", "export", (char *)device, NULL};
    int status = diag_run(argv, 3);
    if (dup2(saved, 1) < 0) _exit(126);
    close(saved);
    ssize_t n = pread(fd, output, size - 1, 0);
    close(fd);
    if (status || n < 0 || (size_t)n >= size - 1) return -1;
    output[n] = 0;
    return 0;
}

static int lab_storage(void)
{
    DIR *devices = opendir("/sys/class/block");
    if (!devices) return -1;
    unsigned matches = 0, scanned = 0;
    int selected = 0, ambiguous = 0;
    struct dirent *entry;
    char path[512], output[4096];
    while ((entry = readdir(devices))) {
        if (entry->d_name[0] == '.') continue;
        snprintf(path, sizeof(path), "/sys/class/block/%s/partition", entry->d_name);
        if (access(path, F_OK)) continue;
        if (++scanned > 64) { ambiguous = 1; break; }
        snprintf(path, sizeof(path), "/dev/%s", entry->d_name);
        if (identify(path, output, sizeof(output))) { ambiguous = 1; continue; }
        if (strstr(output, "UUID=00029cdd-1748-4d2f-b73b-8e8164922098\n") ||
            strstr(output, "PART_ENTRY_UUID=24bd14b9-9d92-490a-ad15-a59c6b8e7cd9\n")) {
            ++matches;
            selected = !strcmp(path, "/dev/nvme0n1p4") && !diag_identity(output);
        }
    }
    closedir(devices);
    if (ambiguous || matches != 1 || !selected) return -1;
    if (identify("/dev/nvme0n1p4", output, sizeof(output)) || diag_identity(output)) return -1;
    struct stat device, target;
    if (lstat("/dev/nvme0n1p4", &device) || !S_ISBLK(device.st_mode)) return -1;
    if (mount("/dev/nvme0n1p4", "/mnt/lab", "ext4", MS_NODEV | MS_NOSUID | MS_NOEXEC, NULL)) return -1;
    mounted = 1;
    if (stat("/mnt/lab", &target) || target.st_dev != device.st_rdev) return -1;
    int parent = open("/mnt/lab", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (parent < 0) return -1;
    char id[100], name[128];
    if (read_text("/proc/sys/kernel/random/boot_id", id, sizeof(id))) { close(parent); return -1; }
    id[strcspn(id, "\n")] = 0;
    if (strlen(id) != 36 || strspn(id, "0123456789abcdef-") != 36) { close(parent); return -1; }
    snprintf(name, sizeof(name), "native-diag-001-%s", id);
    run = diag_new_run(parent, name);
    if (run >= 0 && fsync(parent)) { close(run); run = -1; }
    close(parent);
    return run < 0 ? -1 : 0;
}

int main(void)
{
    if (getpid() != 1) { dprintf(2, "Diagnostic entry requires PID 1\n"); return 77; }
    /* /proc is needed to read the kernel opt-in; no block/module side effects yet. */
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL)) hold();
    char command[8192];
    struct utsname kernel;
    if (uname(&kernel) || read_text("/proc/cmdline", command, sizeof(command)) ||
        diag_gate(1, kernel.release, command)) {
        dprintf(2, "DIAGNOSTIC_GUARD_REFUSED\n"); hold();
    }
    umask(077);
    if (mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) ||
        mount("devtmpfs", "/dev", "devtmpfs", MS_NOSUID | MS_NOEXEC, NULL)) hold();
    ram = open("/run/diagnostic.log", O_RDWR | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (ram < 0 || dup2(ram, 1) < 0 || dup2(ram, 2) < 0) hold();
    dprintf(1, "NATIVE_DIAGNOSTIC_BEGIN release=%s cmdline=%s\n", kernel.release, command);
    /* Best effort only: cannot recover a kernel hard lock; no watchdog alteration. */
    pid_t deadline = fork();
    if (deadline < 0) hold();
    if (!deadline) { sleep(180); reboot(RB_AUTOBOOT); hold(); }
    char *nvme[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", "nvme", NULL};
    int status = probe("nvme", nvme, 15);
    if (!status) {
        int storage = lab_storage();
        dprintf(1, "LAB_STORAGE status=%d\n", storage);
        snapshot();
        if (!storage) {
            const char *modules[] = {"huawei_gaokun_ec", "panel_himax_hx83121a", "msm", "i2c_hid_of"};
            for (unsigned i = 0; i < sizeof(modules) / sizeof(modules[0]); ++i) {
                char *argv[] = {"/sbin/modprobe", "--config", "/etc/modprobe.d", (char *)modules[i], NULL};
                status = probe(modules[i], argv, 15);
                if (status == 124 || status == 125) break;
            }
            if (status != 124 && status != 125) {
                char *enumerate[] = {"/bin/busybox", "sh", "-c",
                    "echo DEVICE_TREE; /bin/busybox cat /proc/device-tree/model; "
                    "echo; echo INPUT; /bin/busybox cat /proc/bus/input/devices; "
                    "echo DRM; for f in /sys/class/drm/card*-*/status /sys/class/drm/card*-*/modes; do "
                    "[ ! -f \"$f\" ] || { echo \"$f\"; /bin/busybox cat \"$f\"; }; done; "
                    "echo DEVICES; /bin/busybox ls -l /dev/dri /dev/input", NULL};
                (void)probe("enumeration", enumerate, 10);
            }
        }
    }
    char *dmesg[] = {"/bin/busybox", "dmesg", NULL};
    (void)probe("kernel-log", dmesg, 5);
    dprintf(1, "NATIVE_DIAGNOSTIC_END desktop_verified=0\n");
    snapshot();
    if (run >= 0) { close(run); run = -1; }
    if (mounted && umount("/mnt/lab")) dprintf(2, "LAB_UNMOUNT_FAILED errno=%d\n", errno);
    /* Deadline remains a best-effort fallback if unmount itself stalls. */
    reboot(RB_AUTOBOOT);
    hold();
    return 1;
}
