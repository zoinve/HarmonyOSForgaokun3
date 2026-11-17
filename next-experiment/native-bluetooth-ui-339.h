#ifndef NATIVE_BLUETOOTH_UI_339_H
#define NATIVE_BLUETOOTH_UI_339_H
#include <poll.h>
#include <sys/prctl.h>
#include <sys/vfs.h>

struct bt339_context {pid_t target;int output;uid_t uid;gid_t gid;};
static int bt339_same(const struct stat *a,const struct stat *b)
{return a->st_dev==b->st_dev && a->st_ino==b->st_ino;}

static void bt339_worker(void *opaque)
{
    const struct bt339_context *context=opaque;
    if(dup2(context->output,1)<0||dup2(context->output,2)<0)_exit(120);
    const char *names[]={"net","mnt","pid"};
    const int types[]={CLONE_NEWNET,CLONE_NEWNS,CLONE_NEWPID};
    int namespaces[3];struct stat wanted[3],own,rootstat,after;
    char path[96];
    snprintf(path,sizeof(path),"/proc/%d/root",context->target);
    int root=open(path,O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    if(root<0||fstat(root,&rootstat))_exit(121);
    for(unsigned i=0;i<3;++i){
        snprintf(path,sizeof(path),"/proc/%d/ns/%s",context->target,names[i]);
        namespaces[i]=open(path,O_RDONLY|O_CLOEXEC);
        snprintf(path,sizeof(path),"/proc/self/ns/%s",names[i]);
        if(namespaces[i]<0||fstat(namespaces[i],&wanted[i])||stat(path,&own)||
           bt339_same(&own,&wanted[i]))_exit(122);
    }
    for(unsigned i=0;i<3;++i){if(setns(namespaces[i],types[i]))_exit(123);close(namespaces[i]);}
    int parent=syscall(SYS_pidfd_open,getpid(),0);
    if(parent<0)_exit(124);
    pid_t child=fork();if(child<0)_exit(124);
    if(!child){
        struct pollfd alive={parent,POLLIN,0};
        if(prctl(PR_SET_PDEATHSIG,SIGKILL)||poll(&alive,1,0)!=0||
           fchdir(root)||chroot(".")||chdir("/"))_exit(125);
        if(stat("/",&after)||!bt339_same(&after,&rootstat))_exit(126);
        for(unsigned i=0;i<3;++i){
            snprintf(path,sizeof(path),"/proc/self/ns/%s",names[i]);
            if(stat(path,&after)||!bt339_same(&after,&wanted[i]))_exit(126);
        }
        struct statfs data;
        if(statfs("/data",&data)||data.f_type!=0xef53||getuid()!=context->uid||
           getgid()!=context->gid||syscall(SYS_close_range,3U,~0U,0))_exit(127);
        dprintf(1,"BT339_CONTEXT namespaces_and_root_verified=1 cli_uid=%u cli_gid=%u credentials_unmodified=1\n",
            (unsigned)getuid(),(unsigned)getgid());
        char *const args[]={"/system/bin/aa","start","-b","com.huawei.hmos.settings",
            "-a","com.huawei.hmos.settings.BluetoothSettingsAbility","-m","pc_settings",NULL};
        char *const env[]={"PATH=/system/bin:/vendor/bin","HOME=/",NULL};
        dprintf(1,"BT339_REQUEST original_aa=1 original_ability_permission_checks=1 discovery_not_inferred=1\n");
        execve(args[0],args,env);_exit(128);
    }
    close(parent);close(root);int status;pid_t got;
    do{got=waitpid(child,&status,0);}while(got<0&&errno==EINTR);
    if(got!=child)_exit(129);
    int result=WIFEXITED(status)?WEXITSTATUS(status):128+WTERMSIG(status);
    dprintf(1,"BT339_AA_EXIT status=%d window_and_discovery_not_inferred=1\n",result);
    _exit(result);
}
static void bt339_start(pid_t target)
{
    static int attempted;
    if(attempted||target<2||run<0)return;
    attempted=1;
    int fd=openat(run,"bluetooth339-start.log",O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(fd<0){dprintf(1,"BT339_REFUSED log_errno=%d\n",errno);return;}
    struct bt339_context context={target,fd,getuid(),getgid()};
    int result=commercial_bounded010(bt339_worker,&context,8000);
    int synced=!fsync(fd);close(fd);
    dprintf(1,"BT339_COMMAND_RESULT status=%d log_synced=%d deadline_ms=8000\n",result,synced);
}
#endif
