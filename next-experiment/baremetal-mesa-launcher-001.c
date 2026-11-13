#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <linux/capability.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/sysmacros.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <unistd.h>

#ifndef MESA_ROOT
#define MESA_ROOT "/run/native-mesa-root-001"
#endif
#ifndef MESA_BUNDLE
#define MESA_BUNDLE "/opt/native-mesa-001"
#endif
#ifndef MESA_RENDER
#define MESA_RENDER "/dev/dri/renderD128"
#endif

static int mesa_gate(uid_t uid, const char *release, const char *command)
{
    if (uid || !release || strcmp(release,"7.1.0-rc3-gaokun3-el2") || !command) return -1;
    char *copy=strdup(command), *save=NULL;
    if (!copy) return -1;
    unsigned diagnostic=0,enforcing=0; int bad=0;
    for (char *p=strtok_r(copy," \t\r\n",&save);p;p=strtok_r(NULL," \t\r\n",&save)) {
        if (!strncmp(p,"harmony.diag=",13)) { ++diagnostic; if (strcmp(p,"harmony.diag=1")) bad=1; }
        if (!strncmp(p,"enforcing=",10)) { ++enforcing; if (strcmp(p,"enforcing=1")) bad=1; }
    }
    free(copy);
    return !bad && diagnostic==1 && enforcing==1 ? 0 : -1;
}

static void require(int ok, const char *operation)
{
    if (!ok) { dprintf(2,"NATIVE_MESA001_FAIL operation=%s errno=%d\n",operation,errno); _exit(126); }
}

static void limit_resource(int kind, rlim_t value)
{
    struct rlimit limit={value,value}; require(!setrlimit(kind,&limit),"resource limit");
}

static void directory(const char *path, mode_t mode)
{
    require(!mkdir(path,mode),path);
}

static void plain_node(const char *path, unsigned minor_number)
{
    require(!mknod(path,S_IFCHR|0666,makedev(1,minor_number)),path);
}

static void sandbox(void)
{
    /* This runs as PID 1 in a new PID namespace, not the system's PID 1. */
    require(!prctl(PR_SET_PDEATHSIG,SIGKILL),"parent death signal");
    require(!mount("tmpfs",MESA_ROOT,"tmpfs",MS_NOSUID,"mode=0755,size=64m"),"private RAM root");
    directory(MESA_ROOT "/app",0755);
    require(!mount(MESA_BUNDLE,MESA_ROOT "/app",NULL,MS_BIND,NULL),"private bundle bind");
    require(!mount(NULL,MESA_ROOT "/app",NULL,MS_BIND|MS_REMOUNT|MS_RDONLY|MS_NOSUID|MS_NODEV,NULL),"read-only bundle");
    directory(MESA_ROOT "/proc",0555); directory(MESA_ROOT "/sys",0555);
    require(!mount("proc",MESA_ROOT "/proc","proc",MS_RDONLY|MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL),"PID-private read-only proc");
    require(!mount("sysfs",MESA_ROOT "/sys","sysfs",MS_RDONLY|MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL),"read-only sysfs");
    directory(MESA_ROOT "/dev",0755); directory(MESA_ROOT "/dev/dri",0755);
    struct stat render;
    require(!stat(MESA_RENDER,&render) && S_ISCHR(render.st_mode) && major(render.st_rdev)==226 && minor(render.st_rdev)==128,"exact render node identity");
    require(!mknod(MESA_ROOT "/dev/dri/renderD128",S_IFCHR|0660,render.st_rdev),"private render inode");
    require(!chown(MESA_ROOT "/dev/dri/renderD128",0,65534),"private render group");
    plain_node(MESA_ROOT "/dev/null",3); plain_node(MESA_ROOT "/dev/zero",5);
    plain_node(MESA_ROOT "/dev/random",8); plain_node(MESA_ROOT "/dev/urandom",9);
    directory(MESA_ROOT "/tmp",0700);
    require(!chown(MESA_ROOT "/tmp",65534,65534),"private writable scratch owner");
    require(!chdir(MESA_ROOT) && !chroot(".") && !chdir("/"),"private chroot");
    int null=open("/dev/null",O_RDONLY|O_CLOEXEC);
    require(null>=0 && dup2(null,0)==0,"null stdin");
    require(!syscall(SYS_close_range,3u,~0u,0u),"close inherited descriptors");
    limit_resource(RLIMIT_CORE,0); limit_resource(RLIMIT_AS,512*1024*1024);
    limit_resource(RLIMIT_NPROC,32); limit_resource(RLIMIT_NOFILE,64);
    limit_resource(RLIMIT_CPU,10); limit_resource(RLIMIT_FSIZE,1024*1024);
    for (unsigned capability=0;capability<64;++capability) {
        int present=prctl(PR_CAPBSET_READ,capability,0,0,0);
        if (present<0 && errno==EINVAL) break;
        require(present>=0 && !prctl(PR_CAPBSET_DROP,capability,0,0,0),"drop capability bounding set");
    }
    require(!prctl(PR_CAP_AMBIENT,PR_CAP_AMBIENT_CLEAR_ALL,0,0,0),"clear ambient capabilities");
    require(!setgroups(0,NULL) && !setresgid(65534,65534,65534) && !setresuid(65534,65534,65534),"permanently drop groups and identity");
    /* Credential changes clear this setting; arm it again after dropping identity. */
    require(!prctl(PR_SET_PDEATHSIG,SIGKILL),"rearm parent death signal after credential change");
    struct __user_cap_header_struct header={_LINUX_CAPABILITY_VERSION_3,0};
    struct __user_cap_data_struct caps[2]={{0},{0}};
    require(!syscall(SYS_capset,&header,caps),"clear all capabilities");
    require(!prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0),"no new privileges");
    require(!syscall(SYS_capget,&header,caps) && !caps[0].effective && !caps[0].permitted && !caps[0].inheritable && !caps[1].effective && !caps[1].permitted && !caps[1].inheritable,"verify empty capabilities");
    require(getuid()==65534 && geteuid()==65534 && getgid()==65534 && getegid()==65534 && getgroups(0,NULL)==0 && prctl(PR_GET_NO_NEW_PRIVS,0,0,0,0)==1,"verify non-root admission");
    require(access("/dev/dri/card0",F_OK) && access("/dev/input",F_OK) && access("/dev/nvme0n1",F_OK),"no primary/input/storage device paths");
    dprintf(1,"NATIVE_MESA001_SANDBOX uid=65534 gid=65534 groups=0 caps=0 no_new_privs=1 private_pid_mount_net=1 primary_node_absent=1 policy_loaded_by_probe=0\n");
    char *const argv[]={"/app/lib/ld-musl-aarch64.so.1","--library-path","/app/lib","/app/probe",NULL};
    char *const environment[]={"HOME=/nonexistent","TMPDIR=/tmp","MESA_SHADER_CACHE_DISABLE=true","EGL_LOG_LEVEL=debug","GBM_BACKEND=dri","GBM_BACKENDS_PATH=/app/lib/gbm",NULL};
    execve(argv[0],argv,environment);
    require(0,"explicit OHOS loader exec");
}

int main(void)
{
    struct utsname kernel; char command[8192];
    int fd=open("/proc/cmdline",O_RDONLY|O_CLOEXEC);
    ssize_t size=fd<0?-1:read(fd,command,sizeof(command)-1);
    if (fd>=0) close(fd);
    if (size<=0 || size==(ssize_t)sizeof(command)-1 || uname(&kernel)) return 77;
    command[size]=0;
    if (mesa_gate(geteuid(),kernel.release,command)) {
        dprintf(2,"Native Mesa launcher requires diagnostic kernel and enforcing opt-in\n"); return 77;
    }
    struct stat output,error;
    require(!fstat(1,&output) && !fstat(2,&error) && (S_ISREG(output.st_mode)||S_ISFIFO(output.st_mode)) && (S_ISREG(error.st_mode)||S_ISFIFO(error.st_mode)),"log descriptors must not be devices");
    umask(0);
    require(!mkdir(MESA_ROOT,0700),"exclusive private mountpoint");
    require(!unshare(CLONE_NEWNS|CLONE_NEWNET|CLONE_NEWPID),"new mount network PID namespaces");
    require(!mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL),"private mount propagation");
    pid_t child=fork(); require(child>=0,"namespace init fork");
    if (!child) sandbox();
    int status=0; pid_t done;
    do { done=waitpid(child,&status,0); } while (done<0 && errno==EINTR);
    require(done==child,"wait namespace init");
    require(!umount2(MESA_ROOT,MNT_DETACH) && !rmdir(MESA_ROOT),"remove private mounts and mountpoint");
    int result=WIFEXITED(status)?WEXITSTATUS(status):128+WTERMSIG(status);
    dprintf(1,"NATIVE_MESA001_END status=%d desktop_verified=0\n",result);
    return result;
}
