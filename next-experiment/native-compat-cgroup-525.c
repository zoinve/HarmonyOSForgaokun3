/* Included after the existing target namespace and root-identity guards. */
#include <sys/mount.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <signal.h>
#include <time.h>

static int compat525_put(const char *path, const char *text)
{
    int fd=open(path,O_WRONLY|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0)return -1;
    size_t size=strlen(text);
    ssize_t n=write(fd,text,size);
    int result=n==(ssize_t)size ? 0:-1;
    if(close(fd))result=-1;
    return result;
}

static long long compat525_number(const char *path, const char *field)
{
    char buffer[4096];
    int fd=open(path,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if(fd<0)return -1;
    ssize_t n=read(fd,buffer,sizeof(buffer)-1);
    close(fd);
    if(n<=0 || n==(ssize_t)sizeof(buffer)-1)return -1;
    buffer[n]=0;
    char *save=NULL;
    for(char *line=strtok_r(buffer,"\n",&save);line;line=strtok_r(NULL,"\n",&save)){
        char *value=line;
        if(field){
            size_t size=strlen(field);
            if(strncmp(line,field,size) || line[size]!=' ')continue;
            value=line+size+1;
        }
        char *end=NULL;
        errno=0;
        long long result=strtoll(value,&end,10);
        if(errno || end==value || *end || result<0)return -1;
        return result;
    }
    return -1;
}

static int compat525_probe(void)
{
    struct stat st;
    if(lstat("/compat525",&st) || !S_ISDIR(st.st_mode) || st.st_uid ||
       (st.st_mode&0777)!=0700)return 130;
    if(unshare(CLONE_NEWNS) || mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL))return 131;
    if(mount("compat525","/compat525","tmpfs",MS_NOSUID|MS_NODEV|MS_NOEXEC,"size=64k,mode=0700"))return 132;
    const char *memory="/compat525/memory", *pids="/compat525/pids";
    int mounted_memory=0,mounted_pids=0,made_memory=0,made_pids=0;
    int result=133;
    char memgroup[128],pidgroup[128],path[256],value[64];
    snprintf(memgroup,sizeof(memgroup),"%s/matebook-probe-%ld",memory,(long)getpid());
    snprintf(pidgroup,sizeof(pidgroup),"%s/matebook-probe-%ld",pids,(long)getpid());
    if(mkdir(memory,0700) || mkdir(pids,0700))goto cleanup;
    if(mount("none",memory,"cgroup",MS_NOSUID|MS_NODEV|MS_NOEXEC,"memory"))goto cleanup;
    mounted_memory=1;
    if(mount("none",pids,"cgroup",MS_NOSUID|MS_NODEV|MS_NOEXEC,"pids"))goto cleanup;
    mounted_pids=1;
    if(mkdir(memgroup,0700))goto cleanup;
    made_memory=1;
    if(mkdir(pidgroup,0700))goto cleanup;
    made_pids=1;
    snprintf(path,sizeof(path),"%s/memory.limit_in_bytes",memgroup);
    if(compat525_put(path,"33554432") || compat525_number(path,NULL)!=33554432)goto cleanup;
    /* Prevent swap from turning a bounded memory charge into prolonged IO. */
    snprintf(path,sizeof(path),"%s/memory.memsw.limit_in_bytes",memgroup);
    if(!lstat(path,&st) && compat525_put(path,"33554432"))goto cleanup;
    snprintf(path,sizeof(path),"%s/pids.max",pidgroup);
    if(compat525_put(path,"1") || compat525_number(path,NULL)!=1)goto cleanup;
    int gate[2];
    if(socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,gate))goto cleanup;
    pid_t child=fork();
    if(child<0){close(gate[0]);close(gate[1]);goto cleanup;}
    if(!child){
        close(gate[1]);
        char token;
        if(read(gate[0],&token,1)!=1 || token!='G')_exit(140);
        close(gate[0]);
        struct rlimit limit={96*1024*1024,96*1024*1024};
        if(setrlimit(RLIMIT_AS,&limit) || prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0))_exit(141);
        errno=0;
        pid_t unexpected=fork();
        int saved=errno;
        if(unexpected==0)_exit(142);
        if(unexpected>0){int status;while(waitpid(unexpected,&status,0)<0 && errno==EINTR){};_exit(143);}
        if(saved!=EAGAIN)_exit(144);
        volatile unsigned char *data=malloc(64*1024*1024);
        if(!data)_exit(145);
        for(size_t offset=0;offset<64*1024*1024;offset+=4096)data[offset]=1;
        free((void *)data);
        _exit(146);
    }
    close(gate[0]);
    snprintf(value,sizeof(value),"%ld",(long)child);
    snprintf(path,sizeof(path),"%s/cgroup.procs",memgroup);
    int attached=!compat525_put(path,value);
    snprintf(path,sizeof(path),"%s/cgroup.procs",pidgroup);
    attached=attached && !compat525_put(path,value);
    if(attached){
        if(send(gate[1],"G",1,MSG_NOSIGNAL)!=1)attached=0;
    }
    close(gate[1]);
    int status=0,finished=0,parent_killed=0;
    for(int attempt=0;attempt<100;++attempt){
        pid_t waited=waitpid(child,&status,WNOHANG);
        if(waited==child){finished=1;break;}
        if(waited<0 && errno!=EINTR)break;
        struct timespec delay={0,100000000};
        while(nanosleep(&delay,&delay) && errno==EINTR){}
    }
    if(!finished){
        parent_killed=1;
        kill(child,SIGKILL);
        while(waitpid(child,&status,0)<0 && errno==EINTR){}
    }
    snprintf(path,sizeof(path),"%s/memory.failcnt",memgroup);
    long long failures=compat525_number(path,NULL);
    snprintf(path,sizeof(path),"%s/memory.oom_control",memgroup);
    long long oom_kills=compat525_number(path,"oom_kill");
    snprintf(path,sizeof(path),"%s/pids.events",pidgroup);
    long long pid_denials=compat525_number(path,"max");
    int memory_ok=attached && finished && !parent_killed && WIFSIGNALED(status) &&
        WTERMSIG(status)==SIGKILL && failures>0 && oom_kills>0;
    int pids_ok=attached && pid_denials>0;
    dprintf(1,"COMPAT525_LIMITS memory_enforced=%d pids_enforced=%d memory_failcnt=%lld oom_kills=%lld pids_denials=%lld parent_killed=%d app_execution_verified=0\n",
            memory_ok,pids_ok,failures,oom_kills,pid_denials,parent_killed);
    result=memory_ok && pids_ok ? 0:134;
cleanup:
    {
        int saved=errno,clean=1;
        if(made_pids && rmdir(pidgroup))clean=0;
        if(made_memory && rmdir(memgroup))clean=0;
        if(mounted_pids && umount(pids))clean=0;
        if(mounted_memory && umount(memory))clean=0;
        if(umount("/compat525"))clean=0;
        dprintf(1,"COMPAT525_END result=%d errno=%d cleanup_complete=%d private_mount_namespace=1 target_dev_mounts_changed=0\n",result,result ? saved:0,clean);
        return clean ? result:135;
    }
}
