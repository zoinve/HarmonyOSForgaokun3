#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

/* The proc mount is pinned before official init moves the root filesystem. */
static int enter_account_root(int procfd)
{
    int rootfd = openat(procfd, "1/root", O_RDONLY | O_DIRECTORY | O_CLOEXEC);
    if (rootfd < 0) return -1;
    int result = fchdir(rootfd) || chroot(".") || chdir("/");
    close(rootfd);
    return result;
}

/* A bounded caller of the original account CLI, not a replacement service. */
static int call(const char *stage, char *const args[])
{
    printf("ACCOUNT960_BEGIN %s\n", stage); fflush(stdout);
    pid_t pid = fork();
    if (pid == 0) {
        alarm(30);
        execv(args[0], args);
        perror("account exec"); _exit(127);
    }
    if (pid < 0) { perror("account fork"); return -1; }
    int status;
    while (waitpid(pid, &status, 0) < 0) {
        if (errno != EINTR) { perror("account wait"); return -1; }
    }
    printf("ACCOUNT960_END %s status=%d\n", stage, status); fflush(stdout);
    return status;
}

int main(void)
{
    if (getpid() != 1) return 2;
    int procfd = -1;
    if (!mkdir("/lab-account-proc", 0700)) {
        if (!mount("proc", "/lab-account-proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL)) {
            procfd = open("/lab-account-proc", O_PATH | O_DIRECTORY | O_CLOEXEC);
            if (umount2("/lab-account-proc", MNT_DETACH)) {
                perror("account proc detach");
                if (procfd >= 0) close(procfd);
                procfd = -1;
            }
        } else perror("account proc mount");
        if (rmdir("/lab-account-proc")) perror("account proc directory");
    } else perror("account proc mkdir");
    if (procfd >= 0) {
        pid_t observer = fork();
        if (observer == 0) {
            sleep(120);
            if (enter_account_root(procfd)) { perror("account root descriptor"); _exit(4); }
            close(procfd);
            setenv("PATH", "/system/bin:/bin", 1);
            printf("ACCOUNT960_CALLER uid=%d gid=%d\n", getuid(), getgid()); fflush(stdout);
            char *help[] = {"/system/bin/acm", "create", "-h", NULL};
            char *before[] = {"/system/bin/acm", "dump", "-a", NULL};
            char *create[] = {"/system/bin/acm", "create", "-n", "labuser", "-s", "labuser", "-t", "normal", NULL};
            call("help", help);
            if (call("before", before) == 0) call("create-normal", create);
            call("after", before);
            puts("ACCOUNT960_DONE password_not_set=1 switch_not_attempted=1"); fflush(stdout);
            _exit(0);
        }
        if (observer < 0) perror("observer fork");
        close(procfd);
    }
    /* Diagnostic failure must never prevent the unmodified official init. */
    char *original[] = {"/init", NULL};
    execv(original[0], original);
    perror("original init"); return 127;
}
