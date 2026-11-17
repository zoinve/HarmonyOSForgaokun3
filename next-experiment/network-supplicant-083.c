#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <sys/wait.h>
#include <unistd.h>

static int same(const struct stat *a, const struct stat *b)
{
    return a->st_dev == b->st_dev && a->st_ino == b->st_ino;
}

static int mode_valid(const char *mode)
{
    const char *modes[] = {"start", "ping", "scan", "scan_results", "status", "log"};
    for (unsigned i = 0; i < sizeof(modes) / sizeof(modes[0]); ++i)
        if (!strcmp(mode, modes[i])) return 1;
    return 0;
}

static int run_mode(const char *mode)
{
    if (!strcmp(mode, "log")) {
        int fd = open("/data/local/tmp/wpa_ctrl/supplicant.log", O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (fd < 0) return 80;
        char buffer[4096];
        unsigned total = 0;
        while (total < 65536) {
            ssize_t n = read(fd, buffer, sizeof(buffer));
            if (n < 0 && errno == EINTR) continue;
            if (n < 0) { close(fd); return 81; }
            if (!n) break;
            if (write(1, buffer, (size_t)n) != n) { close(fd); return 82; }
            total += (unsigned)n;
        }
        close(fd);
        dprintf(1, "NETWORK083_SUPPLICANT_LOG bytes=%u complete_not_inferred=1\n", total);
        return 0;
    }
    char *start[] = {"/network083/lib/ld-linux-aarch64.so.1", "--library-path",
        "/network083/usr/lib/aarch64-linux-gnu", "/network083/usr/sbin/wpa_supplicant",
        "-B", "-Dnl80211", "-iwlan0", "-c/network083/wpa.conf",
        "-P/data/local/tmp/wpa_ctrl/supplicant.pid", "-f/data/local/tmp/wpa_ctrl/supplicant.log", NULL};
    char *query[] = {"/network083/lib/ld-linux-aarch64.so.1", "--library-path",
        "/network083/usr/lib/aarch64-linux-gnu", "/network083/usr/sbin/wpa_cli",
        "-p", "/data/local/tmp/wpa_ctrl", "-i", "wlan0", (char *)mode, NULL};
    if (!strcmp(mode, "start")) {
        struct stat st;
        struct statfs fs;
        if (statfs("/data", &fs) || fs.f_type != 0xef53 ||
            lstat("/data/local/tmp", &st) || !S_ISDIR(st.st_mode)) return 83;
        const char *dir = "/data/local/tmp/wpa_ctrl";
        if (mkdir(dir, 0770) && errno != EEXIST) return 84;
        if (lstat(dir, &st) || !S_ISDIR(st.st_mode) ||
            chown(dir, 0, 1010) || chmod(dir, 0770)) return 85;
        execv(start[0], start);
    } else {
        execv(query[0], query);
    }
    dprintf(2, "NETWORK083_EXEC_FAILED mode=%s errno=%d\n", mode, errno);
    return 86;
}

int main(int argc, char **argv)
{
    if (argc != 3 || !mode_valid(argv[2])) return 64;
    char *end = NULL;
    errno = 0;
    long pid = strtol(argv[1], &end, 10);
    if (errno || !end || *end || pid <= 1 || pid > 2147483647) return 64;
    if (getuid() != 0) return 65;
    const char *names[] = {"net", "mnt", "pid"};
    const int kinds[] = {CLONE_NEWNET, CLONE_NEWNS, CLONE_NEWPID};
    int fds[3];
    struct stat wanted[3], before[3], rootstat;
    char path[96];
    snprintf(path, sizeof(path), "/proc/%ld/root", pid);
    int root = open(path, O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (root < 0 || fstat(root, &rootstat)) return 66;
    for (unsigned i = 0; i < 3; ++i) {
        snprintf(path, sizeof(path), "/proc/%ld/ns/%s", pid, names[i]);
        fds[i] = open(path, O_RDONLY | O_CLOEXEC);
        snprintf(path, sizeof(path), "/proc/self/ns/%s", names[i]);
        if (fds[i] < 0 || fstat(fds[i], &wanted[i]) || stat(path, &before[i]) ||
            same(&before[i], &wanted[i])) return 67;
    }
    for (unsigned i = 0; i < 3; ++i) {
        if (setns(fds[i], kinds[i])) {
            dprintf(2, "NETWORK083_SETNS_FAILED namespace=%s errno=%d\n", names[i], errno);
            return 68;
        }
        close(fds[i]);
    }
    pid_t worker = fork();
    if (worker < 0) return 69;
    if (!worker) {
        if (fchdir(root) || chroot(".") || chdir("/")) _exit(70);
        close(root);
        struct stat after;
        if (stat("/", &after) || !same(&after, &rootstat)) _exit(71);
        for (unsigned i = 0; i < 3; ++i) {
            snprintf(path, sizeof(path), "/proc/self/ns/%s", names[i]);
            if (stat(path, &after) || !same(&after, &wanted[i])) _exit(72);
        }
        dprintf(1, "NETWORK083_TARGET_CONTEXT pid=%ld net_inode=%llu mnt_inode=%llu pid_inode=%llu root_verified=1 mode=%s connectivity_not_inferred=1\n",
                pid, (unsigned long long)wanted[0].st_ino, (unsigned long long)wanted[1].st_ino,
                (unsigned long long)wanted[2].st_ino, argv[2]);
        _exit(run_mode(argv[2]));
    }
    close(root);
    int status;
    while (waitpid(worker, &status, 0) < 0) {
        if (errno != EINTR) return 73;
    }
    return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
}
