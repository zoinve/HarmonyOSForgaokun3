#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (argc != 2) return 64;
    char *end = NULL;
    errno = 0;
    long pid = strtol(argv[1], &end, 10);
    if (errno || !end || *end || pid <= 1 || pid > 2147483647) return 64;
    char path[80];
    snprintf(path, sizeof(path), "/proc/%ld/ns/net", pid);
    int source = open("/proc/self/ns/net", O_RDONLY | O_CLOEXEC);
    int target = open(path, O_RDONLY | O_CLOEXEC);
    struct stat before, wanted, after;
    if (source < 0 || target < 0 || fstat(source, &before) || fstat(target, &wanted)) {
        dprintf(2, "NETWORK082_NAMESPACE_OPEN_FAILED errno=%d\n", errno);
        return 71;
    }
    if (before.st_dev == wanted.st_dev && before.st_ino == wanted.st_ino) {
        dprintf(2, "NETWORK082_NAMESPACE_REFUSED source_equals_target=1\n");
        return 72;
    }
    if (setns(target, CLONE_NEWNET)) {
        dprintf(2, "NETWORK082_SETNS_FAILED errno=%d\n", errno);
        return 73;
    }
    close(source);
    close(target);
    if (stat("/proc/self/ns/net", &after) || after.st_dev != wanted.st_dev ||
        after.st_ino != wanted.st_ino) return 74;
    dprintf(1, "NETWORK082_NAMESPACE_JOINED pid=%ld source_inode=%llu target_inode=%llu connectivity_not_inferred=1\n",
            pid, (unsigned long long)before.st_ino, (unsigned long long)after.st_ino);
    char *args[] = {"/network082/lib/ld-linux-aarch64.so.1", "--library-path",
        "/network082/usr/lib/aarch64-linux-gnu", "/network082/usr/sbin/iw", "dev", NULL};
    execv(args[0], args);
    dprintf(2, "NETWORK082_IW_EXEC_FAILED errno=%d\n", errno);
    return 75;
}
