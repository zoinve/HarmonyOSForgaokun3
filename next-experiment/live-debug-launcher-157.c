/* Sidecar SSH supervision, separate from original HarmonyOS service identities. */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <ifaddrs.h>
#include <limits.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/sysmacros.h>
#include <sys/vfs.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define ROOT157 "/live-debug157-root"
#define KEY157 "/mnt/ubuntu/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-156/root/etc/diag/host_ed25519"
#define ADDRESS157 "192.168.10.210"

static volatile sig_atomic_t stop157;
struct context157 { int net; ino_t net_inode; long target; };

static void stop_handler157(int signo) { (void)signo; stop157 = 1; }

static long long now157(void)
{
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now)) return -1;
    return (long long)now.tv_sec * 1000 + now.tv_nsec / 1000000;
}

static int number157(const char *text, long *value)
{
    if (!text || !text[0] || text[0] == '0' || strspn(text,"0123456789") != strlen(text)) return -1;
    errno = 0;
    char *end;
    long n = strtol(text, &end, 10);
    if (errno || *end || n < 2 || n > INT_MAX) return -1;
    *value = n;
    return 0;
}

static int optin157(void)
{
    char text[4096];
    int fd = open("/proc/cmdline", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return 0;
    ssize_t count = read(fd, text, sizeof(text) - 1);
    close(fd);
    if (count <= 0 || count >= (ssize_t)sizeof(text) - 1) return 0;
    text[count] = 0;
    if (!strstr(text,"harmony.native_original=1") || !strstr(text,"harmony.live_debug157=1")) return 0;
    fd = open("/sys/firmware/devicetree/base/model", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return 0;
    count = read(fd, text, sizeof(text) - 1);
    close(fd);
    if (count <= 0) return 0;
    text[count] = 0;
    return strstr(text,"Matebook E Go") != NULL;
}

static int bind_log157(int fd, const char *destination)
{
    struct stat source, target;
    if (fstat(fd, &source) || !S_ISREG(source.st_mode) ||
        lstat(destination, &target) || !S_ISREG(target.st_mode) || target.st_size) return -1;
    char path[64];
    snprintf(path, sizeof(path), "/proc/self/fd/%d", fd);
    if (mount(path,destination,NULL,MS_BIND,NULL) ||
        mount(NULL,destination,NULL,MS_REMOUNT | MS_BIND | MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC,NULL)) return -1;
    struct statvfs flags;
    if (statvfs(destination, &flags) || !(flags.f_flag & ST_RDONLY)) return -1;
    return 0;
}

static int key_copy157(void)
{
    int fd = open(KEY157, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    struct stat metadata;
    if (fd < 0) return -1;
    if (fstat(fd, &metadata) || !S_ISREG(metadata.st_mode) || metadata.st_uid ||
        (metadata.st_mode & 0077) || metadata.st_size < 100 || metadata.st_size > 4096) { close(fd); return -1; }
    int out = open(ROOT157 "/etc/diag/host_ed25519",O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC,0600);
    if (out < 0) { close(fd); return -1; }
    char data[4096];
    ssize_t n = pread(fd,data,(size_t)metadata.st_size,0);
    int okay = n == metadata.st_size;
    if (okay) okay = write(out,data,(size_t)n) == n;
    explicit_bzero(data,sizeof(data));
    close(out);
    close(fd);
    return okay ? 0 : -1;
}

static int address157(void)
{
    struct ifaddrs *head = NULL;
    if (getifaddrs(&head)) return 0;
    int found = 0;
    unsigned scanned = 0;
    for (struct ifaddrs *it = head; it && scanned++ < 128; it = it->ifa_next) {
        if (!it->ifa_addr || it->ifa_addr->sa_family != AF_INET || strcmp(it->ifa_name,"wlan0")) continue;
        char address[INET_ADDRSTRLEN];
        if (inet_ntop(AF_INET,&((struct sockaddr_in *)it->ifa_addr)->sin_addr,address,sizeof(address)) &&
            !strcmp(address,ADDRESS157)) found = 1;
    }
    freeifaddrs(head);
    return found;
}

static int worker157(void *opaque)
{
    struct context157 *context = opaque;
    signal(SIGTERM, stop_handler157);
    if (prctl(PR_SET_PDEATHSIG,SIGKILL) || mount(NULL,"/",NULL,MS_REC | MS_PRIVATE,NULL) ||
        setns(context->net,CLONE_NEWNET)) return 90;
    close(context->net);
    struct stat actual;
    if (stat("/proc/self/ns/net",&actual) || actual.st_ino != context->net_inode || getpid() != 1) return 91;
    long long began = now157();
    while (!address157()) {
        long long now = now157();
        if (stop157 || now < began || began < 0 || now - began >= 15000) return 92;
        struct timespec pause = {0,100000000};
        nanosleep(&pause,NULL);
    }
    if (bind_log157(196,ROOT157 "/logs/hilog") || bind_log157(197,ROOT157 "/logs/native") || key_copy157()) return 93;
    close(196);
    close(197);
    if (mknod(ROOT157 "/dev/null",S_IFCHR | 0666,makedev(1,3)) || chmod(ROOT157 "/dev/null",0666)) return 94;
    if (chdir(ROOT157) || chroot(".") || chdir("/")) return 95;
    dprintf(1,"LIVE157_CONTEXT target=%ld net_inode=%llu separate_mount_pid_namespaces=1 readonly_logs=1 pid1=1 address=" ADDRESS157 " port=22257\n",
        context->target,(unsigned long long)context->net_inode);
    pid_t daemon = fork();
    if (daemon < 0) return 96;
    if (!daemon) {
        char *const args[] = {"/usr/sbin/sshd","-D","-e","-f","/etc/ssh/sshd_config",NULL};
        char *const env[] = {"PATH=/usr/sbin:/usr/bin:/bin","LANG=C",NULL};
        execve(args[0],args,env);
        _exit(97);
    }
    dprintf(1,"LIVE157_SERVER_SPAWNED pid=%d authentication_not_inferred=1 lifetime_seconds=90\n",daemon);
    long long start = now157();
    while (!stop157) {
        int state;
        pid_t got = waitpid(daemon,&state,WNOHANG);
        if (got == daemon) return WIFEXITED(state) ? WEXITSTATUS(state) : 98;
        if (got < 0 && errno != EINTR) return 98;
        while ((got = waitpid(-1,&state,WNOHANG)) > 0) {
            if (got == daemon) return WIFEXITED(state) ? WEXITSTATUS(state) : 98;
        }
        long long now = now157();
        if (start < 0 || now < start || now - start >= 90000) break;
        struct timespec pause = {0,100000000};
        nanosleep(&pause,NULL);
    }
    dprintf(1,"LIVE157_NAMESPACE_END bounded_cleanup=1\n");
    /* Returning from this PID namespace's init kills every remaining SSH session. */
    return 0;
}

int main(int argc, char **argv)
{
    long target;
    if (argc != 3 || strcmp(argv[1],"--native-live157") || number157(argv[2],&target) ||
        getuid() || !optin157()) return 77;
    struct stat root, source;
    struct statfs filesystem;
    if (lstat(ROOT157,&root) || !S_ISDIR(root.st_mode) || root.st_uid ||
        (root.st_mode & 0077) || statfs(ROOT157,&filesystem) ||
        ((unsigned long)filesystem.f_type != 0x01021994UL && (unsigned long)filesystem.f_type != 0x858458f6UL)) return 78;
    char path[128];
    snprintf(path,sizeof(path),"/proc/%ld/root/system/bin/init",target);
    if (stat(path,&source) || !S_ISREG(source.st_mode)) return 79;
    snprintf(path,sizeof(path),"/proc/%ld/ns/net",target);
    struct context157 context = {.net=open(path,O_RDONLY | O_CLOEXEC),.target=target};
    if (context.net < 0 || fstat(context.net,&source) || stat("/proc/self/ns/net",&root) ||
        source.st_ino == root.st_ino) return 80;
    context.net_inode = source.st_ino;
    clearenv();
    static char stack[1024 * 1024] __attribute__((aligned(16)));
    pid_t worker = clone(worker157,stack + sizeof(stack),CLONE_NEWPID | CLONE_NEWNS | SIGCHLD,&context);
    close(context.net);
    if (worker < 0) return 81;
    signal(SIGTERM,stop_handler157);
    long long start = now157();
    for (;;) {
        int state;
        pid_t got = waitpid(worker,&state,WNOHANG);
        if (got == worker) {
            int status = WIFEXITED(state) ? WEXITSTATUS(state) : 128 + WTERMSIG(state);
            dprintf(1,"LIVE157_END status=%d namespace_reaped=1\n",status);
            return status;
        }
        long long now = now157();
        if (stop157 || (got < 0 && errno != EINTR) || start < 0 || now < start || now - start >= 115000) {
            kill(worker,SIGKILL);
            (void)waitpid(worker,&state,WNOHANG);
            dprintf(1,"LIVE157_END status=124 namespace_kill_requested=1\n");
            return 124;
        }
        struct timespec pause = {0,100000000};
        nanosleep(&pause,NULL);
    }
}
