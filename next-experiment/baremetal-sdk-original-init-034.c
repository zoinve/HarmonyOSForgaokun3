#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/fs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>

static void fail(const char *message)
{
    dprintf(2, "ORIGINAL_INIT034_FAIL %s errno=%d\n", message, errno);
    sync();
    reboot(RB_POWER_OFF);
    for (;;) pause();
}

static void directory(const char *path, mode_t mode)
{
    if (mkdir(path, mode) && errno != EEXIST) fail(path);
}

static ssize_t read_path(const char *path, char *buffer, size_t size)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buffer, size - 1);
    close(fd);
    if (n >= 0) buffer[n] = 0;
    return n;
}

static int option(const char *cmdline, const char *wanted)
{
    size_t n = strlen(wanted);
    for (const char *p = cmdline; *p;) {
        p += strspn(p, " \n\t");
        size_t length = strcspn(p, " \n\t");
        if (length == n && !strncmp(p, wanted, n)) return 1;
        p += length;
    }
    return 0;
}

static void readonly_image(const char *name, const char *target)
{
    char path[128], identity[128];
    snprintf(path, sizeof(path), "/sys/class/block/%s/dev", name);
    unsigned major_number = 0, minor_number = 0;
    int found = 0;
    for (unsigned i = 0; i < 100; ++i) {
        if (read_path(path, identity, sizeof(identity)) > 0 &&
            sscanf(identity, "%u:%u", &major_number, &minor_number) == 2) {
            found = 1;
            break;
        }
        usleep(20000);
    }
    if (!found) fail("read-only image not enumerated");
    snprintf(path, sizeof(path), "/dev/%s", name);
    struct stat st;
    if (lstat(path, &st)) {
        if (mknod(path, S_IFBLK | 0400, makedev(major_number, minor_number))) fail("image node");
    } else if (!S_ISBLK(st.st_mode) || st.st_rdev != makedev(major_number, minor_number)) {
        fail("unexpected image node");
    }
    int fd = open(path, O_RDONLY | O_CLOEXEC), read_only = 0;
    if (fd < 0 || ioctl(fd, BLKROGET, &read_only) || read_only != 1) fail("image must be block read-only");
    close(fd);
    directory(target, 0755);
    /* Original system/vendor mounts permit normal SELinux exec transitions. */
    if (mount(path, target, "ext4", MS_RDONLY | MS_NODEV, "noload")) fail("read-only noload image mount");
    dprintf(1, "ORIGINAL_INIT034_MOUNT device=%s target=%s readonly=1 noload=1\n", name, target);
}

int main(void)
{
    if (getpid() != 1 || getuid() != 0) {
        dprintf(2, "ORIGINAL_INIT034_REFUSED requires isolated PID1/root\n");
        return 77;
    }
    directory("/proc", 0555);
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL)) fail("proc mount");
    char buffer[8192];
    if (read_path("/proc/cmdline", buffer, sizeof(buffer)) <= 0 ||
        !option(buffer, "harmony.original_init_test=1") || !option(buffer, "enforcing=1")) fail("explicit opt-in/enforcing required");
    directory("/sys", 0555);
    if (mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL)) fail("sysfs mount");
    if (read_path("/sys/firmware/devicetree/base/model", buffer, sizeof(buffer)) <= 0 ||
        !strstr(buffer, "dummy-virt")) fail("only disk-isolated QEMU virt allowed");
    directory("/dev", 0755);
    if (mount("devtmpfs", "/dev", "devtmpfs", MS_NOSUID, "mode=0755")) fail("genuine kernel device filesystem");
    int console = open("/dev/console", O_RDWR | O_CLOEXEC);
    if (console < 0) fail("console");
    for (int i = 0; i < 3; ++i) if (dup2(console, i) < 0) fail("console descriptors");
    close(console);
    directory("/sys/fs/selinux", 0755);
    if (mount("selinuxfs", "/sys/fs/selinux", "selinuxfs", MS_NOSUID | MS_NOEXEC, NULL)) fail("SELinux active");
    if (read_path("/sys/fs/selinux/enforce", buffer, sizeof(buffer)) <= 0 || buffer[0] != '1') fail("SELinux enforcing before original init");
    readonly_image("vda", "/usr");
    readonly_image("vdb", "/vendor");
    readonly_image("vdc", "/sys_prod");
    if (symlink("/usr/system", "/system") || symlink("/system/etc", "/etc") ||
        symlink("/system/lib", "/lib") || symlink("/system/lib64", "/lib64") ||
        symlink("/system/bin", "/bin")) fail("original system layout links");
    directory("/data", 0755);
    if (mount("tmpfs", "/data", "tmpfs", MS_NOSUID | MS_NODEV, "mode=0755,size=256m")) fail("volatile data only");
    directory("/run", 0755);
    directory("/tmp", 01777);
    dprintf(1, "ORIGINAL_INIT034_HANDOFF original_init=1 pid=1 readonly_images=3 volatile_data=1 enforcing=1 policy_not_preloaded=1 services_ready=0\n");
    char *const environment[] = {"PATH=/system/bin:/vendor/bin", "HOME=/", NULL};
    char *const arguments[] = {"/system/bin/init", "--second-stage", NULL};
    execve(arguments[0], arguments, environment);
    fail("original init exec");
}
