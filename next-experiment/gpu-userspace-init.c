/* Throwaway diskless init. Only its own diagnostic child may be terminated. */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    mkdir("/proc", 0555); mkdir("/sys", 0555); mkdir("/dev", 0755);
    mount("proc", "/proc", "proc", 0, NULL);
    mount("sysfs", "/sys", "sysfs", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    for (int i = 0; i < 100 && access("/dev/dri/renderD128", F_OK); ++i)
        usleep(100000);
    puts("GPU883_USERSPACE_INIT disks_attached=0");
    pid_t child = fork();
    if (child == 0) {
        setenv("LD_LIBRARY_PATH", "/system/lib64/lab-virgl883:/lib", 1);
        setenv("EGL_LOG_LEVEL", "debug", 1);
        setenv("GBM_BACKENDS_PATH", "/system/lib64/lab-virgl883/gbm", 1);
        execl("/gpu-userspace-probe", "/gpu-userspace-probe", (char *)NULL);
        perror("exec OHOS userspace");
        _exit(125);
    }
    int status = 0, done = 0;
    if (child > 0) {
        for (int i = 0; i < 600; ++i) {
            if (waitpid(child, &status, WNOHANG) == child) { done = 1; break; }
            usleep(100000);
        }
        if (!done) { kill(child, SIGKILL); waitpid(child, &status, 0); }
    }
    printf("GPU883_USERSPACE_EXIT child=%d completed=%d status=%d desktop_not_tested=1\n", child, done, status);
    sync();
    reboot(RB_POWER_OFF);
    for (;;) pause();
}
