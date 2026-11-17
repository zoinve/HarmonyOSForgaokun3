#ifndef SETTINGS_LAUNCH_201_H
#define SETTINGS_LAUNCH_201_H
#include <poll.h>
#include <sys/prctl.h>

struct settings201_context {
    pid_t target;
    int output;
    uid_t uid;
    gid_t gid;
};

static void settings201_worker(void *opaque)
{
    const struct settings201_context *context = opaque;
    const char *names[] = {"mnt", "net", "ipc", "uts", "pid"};
    const int types[] = {CLONE_NEWNS, CLONE_NEWNET, CLONE_NEWIPC, CLONE_NEWUTS, CLONE_NEWPID};
    int namespaces[5], root;
    char path[128];
    if (dup2(context->output,1) < 0 || dup2(context->output,2) < 0) _exit(120);
    for (unsigned i=0;i<5;++i) {
        snprintf(path,sizeof(path),"/proc/%d/ns/%s",context->target,names[i]);
        namespaces[i] = open(path,O_RDONLY|O_CLOEXEC);
        if (namespaces[i] < 0) {
            dprintf(1,"SETTINGS201_REFUSED namespace_index=%u errno=%d\n",i,errno);
            _exit(121);
        }
    }
    struct stat own, target, data;
    if (stat("/proc/self/ns/pid",&own) || fstat(namespaces[4],&target) ||
        (own.st_ino == target.st_ino && own.st_dev == target.st_dev)) _exit(121);
    snprintf(path,sizeof(path),"/proc/%d/root/data",context->target);
    if (stat(path,&data) || data.st_dev != makedev(7,3)) _exit(122);
    snprintf(path,sizeof(path),"/proc/%d/root",context->target);
    root = open(path,O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    if (root < 0) _exit(122);
    for (unsigned i=0;i<5;++i) if (setns(namespaces[i],types[i])) {
        dprintf(1,"SETTINGS201_REFUSED setns_index=%u errno=%d\n",i,errno);
        _exit(123);
    }
    if (fchdir(root) || chroot(".") || chdir("/")) _exit(123);
    int parent = syscall(SYS_pidfd_open,getpid(),0);
    if (parent < 0) _exit(124);
    pid_t launcher = fork();
    if (launcher < 0) _exit(124);
    if (!launcher) {
        struct pollfd alive={parent,POLLIN,0};
        if (prctl(PR_SET_PDEATHSIG,SIGKILL) || poll(&alive,1,0) != 0 ||
            getuid() != context->uid || getgid() != context->gid ||
            syscall(SYS_close_range,3U,~0U,0)) _exit(125);
        dprintf(1,"SETTINGS201_CONTEXT cli_uid=%u cli_gid=%u guest_pid=%d credentials_unmodified=1 application_identity_owned_by_original_services=1\n",
            (unsigned)getuid(),(unsigned)getgid(),getpid());
        char *const args[] = {"/system/bin/aa","start","-b","com.huawei.hmos.settings",
            "-a","com.huawei.hmos.settings.MainAbility","-m","pc_settings",NULL};
        char *const env[] = {"PATH=/system/bin:/vendor/bin","HOME=/",NULL};
        dprintf(1,"SETTINGS201_REQUEST original_aa=1 active_user_selected_by_original_ams=1 fixed_request=1\n");
        execve(args[0],args,env);
        dprintf(1,"SETTINGS201_EXEC_FAILED errno=%d\n",errno);
        _exit(126);
    }
    close(parent);
    int state=0;
    pid_t got;
    do { got=waitpid(launcher,&state,0); } while (got<0 && errno==EINTR);
    if (got != launcher) _exit(127);
    int result=WIFEXITED(state)?WEXITSTATUS(state):128+WTERMSIG(state);
    dprintf(1,"SETTINGS201_AA_EXIT status=%d ability_window_not_inferred=1\n",result);
    _exit(result);
}

static void settings201_start(pid_t target)
{
    static int attempted;
    if (attempted || target < 2 || run < 0) return;
    attempted = 1;
    int fd=openat(run,"settings201-start.log",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if (fd < 0) {
        dprintf(1,"SETTINGS201_REFUSED log_create_errno=%d\n",errno);
        return;
    }
    struct settings201_context context={target,fd,getuid(),getgid()};
    int result=commercial_bounded010(settings201_worker,&context,8000);
    int sync_result=fsync(fd);
    close(fd);
    dprintf(1,"SETTINGS201_COMMAND_RESULT status=%d log_synced=%d deadline_ms=8000 original_runtime_unchanged=1 window_not_inferred=1\n",
        result,!sync_result);
}
#endif
