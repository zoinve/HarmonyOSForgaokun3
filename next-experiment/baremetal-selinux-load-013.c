#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <unistd.h>

static void finish(int success, const char *message)
{
    int saved = errno;
    dprintf(success ? 1 : 2, "SELINUX013_%s %s errno=%d\n",
            success ? "PASS" : "FAIL", message, saved);
    sync();
    reboot(RB_POWER_OFF);
    for (;;) pause();
}

static void require(int ok, const char *message)
{
    if (!ok) finish(0, message);
}

static ssize_t text(const char *path, char *buffer, size_t size)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buffer, size - 1);
    int saved = errno;
    close(fd);
    errno = saved;
    if (n >= 0) buffer[n] = 0;
    return n;
}

int main(void)
{
    if (getpid() != 1 || geteuid() != 0) {
        dprintf(2, "SELinux policy probe requires isolated PID 1\n");
        return 77;
    }
    require(!mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL), "mount proc");
    char buffer[8192];
    require(text("/proc/cmdline", buffer, sizeof(buffer)) > 0, "read opt-in");
    int opted = 0;
    for (char *p = strtok(buffer, " \t\r\n"); p; p = strtok(NULL, " \t\r\n"))
        if (!strcmp(p, "harmony.selinux_test=1")) opted = 1;
    require(opted, "explicit isolated policy opt-in");
    require(!mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL), "mount sysfs");
    require(text("/sys/firmware/devicetree/base/model", buffer, sizeof(buffer)) > 0 &&
            strstr(buffer, "dummy-virt"), "QEMU model required");
    require(!mkdir("/sys/fs/selinux", 0755) || errno == EEXIST, "SELinux mount point");
    require(!mount("selinuxfs", "/sys/fs/selinux", "selinuxfs", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL), "mount selinuxfs");
    require(text("/sys/fs/selinux/enforce", buffer, sizeof(buffer)) > 0 && buffer[0] == '1', "enforcing before policy load");
    int fd = open("/sys/fs/selinux/load", O_WRONLY | O_CLOEXEC);
    require(fd >= 0, "open policy load");
    char invalid[64] = {0};
    errno = 0;
    require(write(fd, invalid, sizeof(invalid)) == -1 && errno == EINVAL, "invalid policy must be rejected");
    close(fd);
    int input = open("/policy.31", O_RDONLY | O_CLOEXEC);
    struct stat st;
    require(input >= 0 && !fstat(input, &st) && S_ISREG(st.st_mode) &&
            st.st_size > 0 && st.st_size <= 32 * 1024 * 1024, "bounded original policy");
    size_t size = (size_t)st.st_size, used = 0;
    unsigned char *policy = malloc(size);
    require(policy != NULL, "allocate original policy buffer");
    while (used < size) {
        ssize_t n = read(input, policy + used, size - used);
        if (n < 0 && errno == EINTR) continue;
        require(n > 0, "read complete policy");
        used += (size_t)n;
    }
    close(input);
    fd = open("/sys/fs/selinux/load", O_WRONLY | O_CLOEXEC);
    require(fd >= 0, "reopen policy load");
    errno = 0;
    ssize_t written = write(fd, policy, size);
    int load_errno = errno;
    dprintf(1, "SELINUX013_LOAD bytes=%zu result=%zd errno=%d\n", size, written, load_errno);
    require(written == (ssize_t)size, "original production policy accepted");
    close(fd);
    free(policy);
    require(text("/sys/fs/selinux/enforce", buffer, sizeof(buffer)) > 0 && buffer[0] == '1', "enforcing after policy load");
    require(text("/proc/self/attr/current", buffer, sizeof(buffer)) > 0, "read current security context");
    dprintf(1, "SELINUX013_CONTEXT %s\n", buffer);
    require(strstr(buffer, ":kernel:") != NULL, "policy-mapped initial kernel domain");
    /* Loading the unchanged production policy is not a service/domain-transition test. */
    finish(1, "original_policy_loaded=1 enforcing=1 invalid_policy_rejected=1 services_not_tested=1 desktop_not_tested=1");
    return 0;
}
