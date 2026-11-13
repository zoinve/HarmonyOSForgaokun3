/* Isolated QEMU-only ABI tests under the unchanged production init domain. */
#include <grp.h>
#include <stdint.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <linux/android/binder.h>

static void original_device_020(const char *name)
{
    char path[256], value[64];
    snprintf(path, sizeof(path), "/sys/class/misc/%s/dev", name);
    require(text(path, value, sizeof(value)) > 0, "actual kernel device identity");
    unsigned major_number, minor_number;
    require(sscanf(value, "%u:%u", &major_number, &minor_number) == 2, "parse actual device numbers");
    snprintf(path, sizeof(path), "/dev/%s", name);
    require(!mknod(path, S_IFCHR | 0666, makedev(major_number, minor_number)) && !chmod(path, 0666),
            "original SDK device mode on isolated RAM node");
    if (!strcmp(name, "access_token_id"))
        require(!chown(path, 3020, 3020), "original SDK token-device owner");
}

static void identity_under_policy_020(void)
{
    const char token_label[] = "u:object_r:dev_at_file:s0";
    const char binder_label[] = "u:object_r:dev_binder_file:s0";
    require(!setxattr("/dev/access_token_id", "security.selinux", token_label, sizeof(token_label), 0) &&
            !setxattr("/dev/binder", "security.selinux", binder_label, sizeof(binder_label), 0),
            "restore original token and Binder device labels");
    char actual[128] = {0};
    require(getxattr("/dev/access_token_id", "security.selinux", actual, sizeof(actual)-1) > 0 &&
            !strcmp(actual, token_label), "actual original token-device label");
    memset(actual, 0, sizeof(actual));
    require(getxattr("/dev/binder", "security.selinux", actual, sizeof(actual)-1) > 0 &&
            !strcmp(actual, binder_label), "actual original Binder-device label");
    int token = open("/dev/access_token_id", O_RDWR | O_CLOEXEC);
    require(token >= 0, "init opens original-labelled actual token device");
    uint64_t self = 0, first = 0, value = 0x1020304050607080ULL, out = 0;
    require(!ioctl(token, _IOR('A', 1, uint64_t), &self) && !ioctl(token, _IOR('A', 3, uint64_t), &first),
            "read actual initial task tokens under enforcing policy");
    require(!ioctl(token, _IOW('A', 2, uint64_t), &value) &&
            !ioctl(token, _IOR('A', 1, uint64_t), &out) && out == value,
            "authorized 64-bit self-token roundtrip under enforcing policy");
    uint32_t version = 0xa5a5a5a5U;
    errno = 0;
    require(ioctl(token, _IOR('A', 25, uint32_t), &version) == -1 && errno == EOPNOTSUPP &&
            version == 0xa5a5a5a5U, "unsupported SPM remains honestly unsupported under policy");
    pid_t child = fork();
    require(child >= 0, "fork actual unprivileged token-denial regression");
    if (!child) {
        if (setgroups(0, NULL) || setgid(1001) || setuid(1001)) _exit(90);
        int own = open("/dev/access_token_id", O_RDWR | O_CLOEXEC);
        if (own < 0) _exit(91);
        uint64_t inherited = 0;
        if (ioctl(own, _IOR('A', 1, uint64_t), &inherited) || inherited != value) _exit(92);
        errno = 0;
        if (ioctl(own, _IOW('A', 2, uint64_t), &inherited) != -1 || errno != EPERM) _exit(93);
        errno = 0;
        if (ioctl(own, _IOR('A', 3, uint64_t), &inherited) != -1 || errno != EPERM) _exit(94);
        close(own);
        _exit(0);
    }
    int status;
    require(waitpid(child, &status, 0) == child && WIFEXITED(status) && WEXITSTATUS(status) == 0,
            "actual non-owner token writes and first-caller reads denied");
    require(!ioctl(token, _IOW('A', 2, uint64_t), &self) &&
            !ioctl(token, _IOR('A', 1, uint64_t), &out) && out == self &&
            !ioctl(token, _IOR('A', 3, uint64_t), &out) && out == first,
            "restore test-only task identity and preserve first caller");
    close(token);
    int binder = open("/dev/binder", O_RDWR | O_CLOEXEC);
    require(binder >= 0, "init opens original-labelled actual Binder device");
    struct binder_version protocol = {0};
    struct { uint64_t bits; } features = {0};
    require(!ioctl(binder, BINDER_VERSION, &protocol) && protocol.protocol_version == 8 &&
            !ioctl(binder, _IOWR('b', 30, features), &features) && features.bits == 5,
            "actual Binder protocol and truthful feature bits under enforcing policy");
    errno = 0;
    require(ioctl(binder, BINDER_SET_CONTEXT_MGR, 0) == -1 && errno == EACCES,
            "production policy must forbid init becoming Binder context manager");
    close(binder);
    dprintf(1, "SELINUX020_IDENTITY_PASS actual_devices=1 original_labels=1 task_token_roundtrip=1 "
               "nonowner_denied=1 spm_unsupported=1 protocol=8 features=5 init_context_manager_denied=1 "
               "services_not_tested=1\n");
}
