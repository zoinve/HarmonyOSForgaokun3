#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

/* A bounded caller of the original account CLI, not a replacement service. */
static int call(const char *stage, char *const args[])
{
    printf("ACCOUNT959_BEGIN %s\n", stage); fflush(stdout);
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
    printf("ACCOUNT959_END %s status=%d\n", stage, status); fflush(stdout);
    return status;
}

int main(void)
{
    if (getpid() != 1) return 2;
    pid_t observer = fork();
    if (observer < 0) { perror("observer fork"); return 3; }
    if (observer == 0) {
        sleep(120);
        if (chdir("/proc/1/root") || chroot(".") || chdir("/")) {
            perror("account root namespace"); _exit(4);
        }
        setenv("PATH", "/system/bin:/bin", 1);
        printf("ACCOUNT959_CALLER uid=%d gid=%d\n", getuid(), getgid()); fflush(stdout);
        char *help[] = {"/system/bin/acm", "create", "-h", NULL};
        char *before[] = {"/system/bin/acm", "dump", "-a", NULL};
        char *create[] = {"/system/bin/acm", "create", "-n", "labuser", "-s", "labuser", "-t", "normal", NULL};
        call("help", help);
        if (call("before", before) == 0) call("create-normal", create);
        call("after", before);
        puts("ACCOUNT959_DONE password_not_set=1 switch_not_attempted=1"); fflush(stdout);
        _exit(0);
    }
    char *original[] = {"/init", NULL};
    execv(original[0], original);
    perror("original init"); return 127;
}
