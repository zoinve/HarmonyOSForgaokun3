/* Run only after the existing namespace/chroot identity checks. */
#include <sys/socket.h>
#include <sys/un.h>

static int share501_run(char *const args[])
{
    pid_t pid = fork();
    if (pid < 0) return 91;
    if (!pid) {
        execv(args[0], args);
        _exit(92);
    }
    int status;
    while (waitpid(pid, &status, 0) < 0) if (errno != EINTR) return 93;
    return WIFEXITED(status) ? WEXITSTATUS(status) : 94;
}

static int share501_wlan(void)
{
    struct stat st;
    int input = open("/network084/wpa.conf", O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if (input < 0) return 95;
    if (fstat(input, &st) || !S_ISREG(st.st_mode) || st.st_uid ||
        (st.st_mode & 0777) != 0400 || st.st_size <= 0 || st.st_size > 65536) {
        close(input); return 96;
    }
    int output = open("/share501/wlan.conf", O_WRONLY|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW, 0400);
    if (output < 0) { close(input); return 97; }
    int result = 0;
    char data[4096];
    for (;;) {
        ssize_t n = read(input, data, sizeof(data));
        if (n < 0 && errno == EINTR) continue;
        if (n < 0) { result = 98; break; }
        if (!n) break;
        ssize_t offset = 0;
        while (offset < n) {
            ssize_t written = write(output, data + offset, (size_t)(n - offset));
            if (written < 0 && errno == EINTR) continue;
            if (written <= 0) { result = 99; break; }
            offset += written;
        }
        if (result) break;
    }
    const char setting[] = "\np2p_disabled=1\n";
    if (!result && write(output, setting, sizeof(setting)-1) != (ssize_t)sizeof(setting)-1) result = 99;
    close(input);
    if (close(output) && !result) result = 99;
    dprintf(1,"SHARE501_WLAN_CONFIG result=%d private_ram_copy=1 credentials_exported=0\n",result);
    return result;
}

static int share501_ping(void)
{
    int fd = socket(AF_UNIX, SOCK_DGRAM|SOCK_CLOEXEC, 0);
    if (fd < 0) return 100;
    struct timeval timeout = {2, 0};
    struct sockaddr_un local = {.sun_family=AF_UNIX}, remote = {.sun_family=AF_UNIX};
    snprintf(local.sun_path+1, sizeof(local.sun_path)-1, "share501-%ld", (long)getpid());
    strcpy(remote.sun_path, "/data/local/tmp/l410_p2p_ctrl/p2p0");
    int ok = !setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)) &&
        !bind(fd,(struct sockaddr *)&local,sizeof(local)) &&
        !connect(fd,(struct sockaddr *)&remote,sizeof(remote)) && send(fd,"PING",4,0)==4;
    char reply[16];
    ssize_t n = ok ? recv(fd,reply,sizeof(reply),0) : -1;
    int saved = errno;
    ok = n==5 && !memcmp(reply,"PONG\n",5);
    close(fd);
    dprintf(1,"SHARE501_PING pong=%d errno=%d transfer_verified=0\n",ok,ok ? 0 : saved);
    return ok ? 0 : 101;
}

static int share501_start(void)
{
    struct stat st;
    if (!lstat("/sys/class/net/p2p0",&st)) return 102;
    if (errno != ENOENT) return 103;
    const char *directory = "/data/local/tmp/l410_p2p_ctrl";
    if (mkdir(directory,0770) && errno != EEXIST) return 104;
    if (lstat(directory,&st) || !S_ISDIR(st.st_mode) || st.st_uid ||
        chown(directory,0,1010) || chmod(directory,0770)) return 105;
    char *add[] = {"/share494/lib/ld-linux-aarch64.so.1","--library-path",
        "/share494/usr/lib/aarch64-linux-gnu","/share494/usr/sbin/iw",
        "dev","wlan0","interface","add","p2p0","type","managed",NULL};
    int result = share501_run(add);
    dprintf(1,"SHARE501_INTERFACE_ADD result=%d real_netdev_required=1\n",result);
    if (result) return result;
    char *start[] = {"/network083/lib/ld-linux-aarch64.so.1","--library-path",
        "/network083/usr/lib/aarch64-linux-gnu","/share501/wpa_supplicant",
        "-B","-Dnl80211","-ip2p0","-c/share501/p2p.conf",
        "-P/data/local/tmp/l410_p2p_ctrl/supplicant.pid",
        "-f/data/local/tmp/l410_p2p_ctrl/supplicant.log",NULL};
    result = share501_run(start);
    dprintf(1,"SHARE501_SUPPLICANT_START result=%d group_connected_not_inferred=1\n",result);
    if (result) return result;
    return share501_ping();
}
