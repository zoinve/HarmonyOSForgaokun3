#define _GNU_SOURCE
#include "baremetal-diagnostic-core.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

int diag_gate(int pid, const char *release, const char *cmdline)
{
    if (pid != 1 || !release || !cmdline ||
        strcmp(release, "7.1.0-rc3-gaokun3-el2")) return -1;
    char *copy = strdup(cmdline), *save = NULL;
    if (!copy) return -1;
    int count = 0, valid = 0;
    for (char *p = strtok_r(copy, " \t\r\n", &save); p;
         p = strtok_r(NULL, " \t\r\n", &save)) {
        if (!strncmp(p, "harmony.diag=", 13)) {
            ++count;
            valid = !strcmp(p, "harmony.diag=1");
        }
    }
    free(copy);
    return count == 1 && valid ? 0 : -1;
}

int diag_identity(const char *exported)
{
    if (!exported) return -1;
    const char *keys[] = {"UUID=", "PART_ENTRY_UUID=", "TYPE="};
    const char *expected[] = {"UUID=00029cdd-1748-4d2f-b73b-8e8164922098",
        "PART_ENTRY_UUID=24bd14b9-9d92-490a-ad15-a59c6b8e7cd9", "TYPE=ext4"};
    unsigned counts[3] = {0};
    char *copy = strdup(exported), *save = NULL;
    if (!copy) return -1;
    int bad = 0;
    for (char *p = strtok_r(copy, "\n", &save); p;
         p = strtok_r(NULL, "\n", &save)) {
        for (unsigned i = 0; i < 3; ++i) {
            if (!strncmp(p, keys[i], strlen(keys[i]))) {
                ++counts[i];
                if (strcmp(p, expected[i])) bad = 1;
            }
        }
    }
    free(copy);
    return !bad && counts[0] == 1 && counts[1] == 1 && counts[2] == 1 ? 0 : -1;
}

int diag_new_run(int parent, const char *name)
{
    if (!name || !*name || strchr(name, '/') || !strcmp(name, ".") ||
        !strcmp(name, "..")) { errno = EINVAL; return -1; }
    if (mkdirat(parent, name, 0700)) return -1;
    return openat(parent, name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
}

static double monotonic(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) return -1;
    return t.tv_sec + t.tv_nsec / 1e9;
}

int diag_run(char *const argv[], unsigned seconds)
{
    double start = monotonic();
    if (start < 0 || !seconds) return 125;
    pid_t child = fork();
    if (child < 0) return 125;
    if (!child) {
        if (setpgid(0, 0)) _exit(126);
        execv(argv[0], argv);
        _exit(127);
    }
    (void)setpgid(child, child);
    for (;;) {
        int status;
        pid_t got = waitpid(child, &status, WNOHANG);
        if (got == child) return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
        if (got < 0 && errno != EINTR) return 125;
        double now = monotonic();
        if (now < 0 || now - start >= seconds) {
            (void)kill(-child, SIGKILL);
            (void)kill(child, SIGKILL);
            /* Never block on an uninterruptible task. 124 does not assert reaping. */
            (void)waitpid(child, &status, WNOHANG);
            return 124;
        }
        struct timespec delay = {.tv_sec = 0, .tv_nsec = 20000000};
        (void)nanosleep(&delay, NULL);
    }
}
