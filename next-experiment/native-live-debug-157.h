#ifndef NATIVE_LIVE_DEBUG_157_H
#define NATIVE_LIVE_DEBUG_157_H
#include <sys/prctl.h>

static pid_t native_live157_pid = -1;

static void native_live157_load(void)
{
    char *args[] = {"/bin/busybox","sh","-c",
        "test ! -e /live-debug157-root/usr && "
        "test \"$(/bin/busybox sha256sum /mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-inputs-157/runtime-root.tar.gz)\" = \""
        LIVE157_ARCHIVE_SHA
        "  /mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-inputs-157/runtime-root.tar.gz\" && "
        "/bin/busybox tar -xzf /mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-inputs-157/runtime-root.tar.gz -C /live-debug157-root",NULL};
    int result = probe("live-debug157-load",args,8);
    dprintf(1,"LIVE157_LOAD status=%d optional_sidecar=1 original_runtime_unchanged=1\n",result);
}

static void native_live157_start(pid_t target)
{
    if (native_live157_pid > 0 || target < 2 || access("/live-debug157-root/usr/sbin/sshd",X_OK)) return;
    int hilog = openat(run,"interactive-hilog030.log",O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    int native = open("/run/diagnostic.log",O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (hilog < 0 || native < 0) {
        if (hilog >= 0) close(hilog);
        if (native >= 0) close(native);
        dprintf(1,"LIVE157_START_REFUSED log_open=1\n");
        return;
    }
    pid_t worker = fork();
    if (!worker) {
        if (prctl(PR_SET_PDEATHSIG,SIGKILL) || dup2(hilog,196) < 0 || dup2(native,197) < 0 ||
            syscall(SYS_close_range,3U,195U,0) || syscall(SYS_close_range,198U,~0U,0)) _exit(99);
        char pid[32];
        snprintf(pid,sizeof(pid),"%d",target);
        char *const args[] = {"/live-debug157","--native-live157",pid,NULL};
        char *const env[] = {"PATH=/bin:/sbin",NULL};
        execve(args[0],args,env);
        _exit(99);
    }
    close(hilog);
    close(native);
    native_live157_pid = worker;
    dprintf(1,"LIVE157_START supervisor=%d target=%d authentication_not_inferred=1\n",worker,target);
}

static void native_live157_stop(void)
{
    if (native_live157_pid < 2) return;
    int state = 0;
    pid_t got = waitpid(native_live157_pid,&state,WNOHANG);
    if (!got) {
        kill(native_live157_pid,SIGTERM);
        for (unsigned i = 0; i < 20; ++i) {
            got = waitpid(native_live157_pid,&state,WNOHANG);
            if (got != 0) break;
            struct timespec pause = {0,10000000};
            nanosleep(&pause,NULL);
        }
        if (!got) {
            kill(native_live157_pid,SIGKILL);
            got = waitpid(native_live157_pid,&state,WNOHANG);
        }
    }
    dprintf(1,"LIVE157_STOP supervisor=%d reaped=%d state=%d\n",native_live157_pid,got == native_live157_pid,state);
    native_live157_pid = -1;
}

#endif
