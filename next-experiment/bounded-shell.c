/* Native, bounded diagnostic command runner; no guest privileges are borrowed. */
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/syscall.h>
#include <linux/capability.h>
#include <unistd.h>
#include <fcntl.h>
#include <grp.h>
#include <signal.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int lab_shell_run(const char *label, const char *command, unsigned limit, const char *shell) {
    fflush(NULL);
    pid_t child = fork();
    if (child < 0) return 125;
    if (!child) {
        if (setsid() < 0 || setgroups(0, NULL) || setresgid(2000,2000,2000) || setresuid(2000,2000,2000)) {
            perror("LAB873_DROP_IDENTITY"); _exit(125);
        }
        struct __user_cap_header_struct header = {_LINUX_CAPABILITY_VERSION_3, 0};
        struct __user_cap_data_struct caps[2] = {{0}};
        if (syscall(SYS_capset, &header, caps)) {perror("LAB873_CLEAR_CAPS"); _exit(125);}
        if (getuid()!=2000 || geteuid()!=2000 || getgid()!=2000 || getegid()!=2000) _exit(125);
        /* A normal shell label, never an inherited root service's identity/token. */
        if (!strcmp(shell,"/system/bin/sh")) {
            const char context[]="u:r:sh:s0";
            int fd=open("/proc/self/attr/exec",O_WRONLY|O_CLOEXEC);
            if (fd<0 || write(fd,context,sizeof(context)-1)!=(ssize_t)sizeof(context)-1) {
                perror("LAB873_SHELL_CONTEXT"); _exit(125);
            }
            close(fd);
        }
        for (int fd=3;fd<1024;fd++) close(fd);
        char *args[]={(char *)shell,"-c",(char *)command,NULL};
        char *env[]={"PATH=/system/bin:/vendor/bin:/bin:/usr/bin","HOME=/data/local/tmp",
            "LD_LIBRARY_PATH=/system/lib64:/system/lib64/platformsdk:/system/lib64/chipset-sdk",NULL};
        execve(shell,args,env);
        perror("LAB873_EXEC_SHELL"); _exit(125);
    }
    printf("LAB873_COMMAND_START label=%s pid=%d limit=%u uid=2000\n",label,child,limit); fflush(stdout);
    int status=0;
    for (unsigned elapsed=0;elapsed<limit;elapsed++) {
        pid_t result=waitpid(child,&status,WNOHANG);
        if (result==child) {
            int rc=WIFEXITED(status)?WEXITSTATUS(status):128+WTERMSIG(status);
            printf("LAB873_COMMAND_RETURN label=%s rc=%d\n",label,rc); fflush(stdout);return rc;
        }
        if (result<0 && errno!=EINTR) return 125;
        sleep(1);
    }
    /* Only this runner's own command group is bounded, never guest services. */
    kill(-child,SIGKILL);kill(child,SIGKILL);
    while (waitpid(child,&status,0)<0 && errno==EINTR) {}
    printf("LAB873_COMMAND_TIMEOUT label=%s limit=%u\n",label,limit);fflush(stdout);return 124;
}

#ifndef BOUNDED_SHELL_LIBRARY
int main(int argc,char **argv) {
    if (argc<3 || argc>4) return 125;
    char *end;unsigned long limit=strtoul(argv[1],&end,10);
    if (*end || !limit || limit>120) return 125;
    return lab_shell_run("native-test",argv[2],(unsigned)limit,argc==4?argv[3]:"/system/bin/sh");
}
#endif
