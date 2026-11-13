"""Copy kernel audit multicast, never register/replace the existing receiver."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-086.py')))
source = parent['source'].replace('ORIGINAL_INIT086_', 'ORIGINAL_INIT087_').replace('GRAPHICS086_', 'GRAPHICS087_')
source = source.replace('graphics_profile_events_086', 'graphics_profile_events_087')
helper = r'''
static int graphics_audit_write_087(int fd, const void *bytes, size_t length)
{
    const unsigned char *cursor = bytes;
    while (length) {
        ssize_t n = write(fd, cursor, length);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) return -1;
        cursor += n;
        length -= (size_t)n;
    }
    return 0;
}

/* AUDIT_NLGRP_READLOG delivers copies; no control request is sent here. */
static void graphics_audit_copy_087(void)
{
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC | SOCK_NONBLOCK, NETLINK_AUDIT);
    if (fd < 0) {
        dprintf(1, "GRAPHICS087_AUDIT_COPY stage=socket errno=%d\n", errno);
        return;
    }
    int desired = 1024 * 1024;
    int buffer_rc = setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &desired, sizeof(desired));
    int buffer_errno = buffer_rc ? errno : 0;
    struct sockaddr_nl local = {.nl_family = AF_NETLINK,
        .nl_groups = 1U << (AUDIT_NLGRP_READLOG - 1)};
    if (bind(fd, (struct sockaddr *)&local, sizeof(local))) {
        dprintf(1, "GRAPHICS087_AUDIT_COPY stage=bind errno=%d\n", errno);
        close(fd);
        return;
    }
    int log = open("/data/graphics-audit-087.log",
                   O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (log < 0) {
        dprintf(1, "GRAPHICS087_AUDIT_COPY stage=file errno=%d\n", errno);
        close(fd);
        return;
    }
    pid_t child = fork();
    if (child != 0) {
        dprintf(1, "GRAPHICS087_AUDIT_COPY stage=fork pid=%ld errno=%d multicast_only=1 receiver_unchanged=1 buffer_rc=%d buffer_errno=%d\n",
                (long)child, child < 0 ? errno : 0, buffer_rc, buffer_errno);
        close(log);
        close(fd);
        return;
    }
    alarm(70);
    struct timespec started, now;
    clock_gettime(CLOCK_MONOTONIC, &started);
    const size_t maximum = 64U * 1024U * 1024U;
    size_t written = 0;
    unsigned records = 0, dropped = 0;
    int final_errno = 0, byte_limit_reached = 0;
    for (;;) {
        clock_gettime(CLOCK_MONOTONIC, &now);
        if (now.tv_sec - started.tv_sec >= 60 || byte_limit_reached) break;
        struct pollfd ready = {.fd = fd, .events = POLLIN};
        int rc = poll(&ready, 1, 1000);
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) { final_errno = errno; break; }
        if (!rc) continue;
        unsigned char bytes[65536] __attribute__((aligned(8)));
        struct sockaddr_nl sender;
        memset(&sender, 0, sizeof(sender));
        struct iovec iov = {.iov_base = bytes, .iov_len = sizeof(bytes)};
        struct msghdr msg = {.msg_name = &sender, .msg_namelen = sizeof(sender),
                             .msg_iov = &iov, .msg_iovlen = 1};
        ssize_t n = recvmsg(fd, &msg, 0);
        if (n < 0 && (errno == EAGAIN || errno == EINTR)) continue;
        if (n < 0 && errno == ENOBUFS) { ++dropped; continue; }
        if (n <= 0) { final_errno = n < 0 ? errno : EIO; break; }
        if ((msg.msg_flags & MSG_TRUNC) || sender.nl_pid != 0) { ++dropped; continue; }
        int remaining = (int)n;
        for (struct nlmsghdr *h = (struct nlmsghdr *)bytes;
             NLMSG_OK(h, remaining); h = NLMSG_NEXT(h, remaining)) {
            size_t length = NLMSG_PAYLOAD(h, 0);
            const unsigned char *body = NLMSG_DATA(h);
            while (length && body[length - 1] == 0) --length;
            if (h->nlmsg_type < 1000) continue;
            char prefix[40];
            int prefix_length = snprintf(prefix, sizeof(prefix), "type=%u ", h->nlmsg_type);
            if (prefix_length <= 0 || prefix_length >= (int)sizeof(prefix) ||
                length + (size_t)prefix_length + 1 > maximum - written) {
                byte_limit_reached = 1;
                break;
            }
            if (graphics_audit_write_087(log, prefix, (size_t)prefix_length) ||
                graphics_audit_write_087(log, body, length) ||
                graphics_audit_write_087(log, "\n", 1)) {
                final_errno = errno ? errno : EIO;
                break;
            }
            written += length + (size_t)prefix_length + 1;
            ++records;
        }
        if (final_errno) break;
        if (remaining && !byte_limit_reached) ++dropped;
    }
    int sync_rc = fsync(log);
    int sync_errno = sync_rc ? errno : 0;
    dprintf(1, "GRAPHICS087_AUDIT_COPY_END records=%u bytes=%zu dropped=%u errno=%d fsync_rc=%d fsync_errno=%d byte_limit_reached=%d bounded_seconds=60 bounded_bytes=67108864\n",
            records, written, dropped, final_errno, sync_rc, sync_errno, byte_limit_reached);
    close(log);
    close(fd);
    _exit(final_errno ? 75 : 0);
}

'''
assert source.count('int main(void)') == 1
source = source.replace('int main(void)', helper + 'int main(void)')
anchor = '    graphics_audit_rule_086();'
assert source.count(anchor) == 1
source = source.replace(anchor, '    graphics_audit_copy_087();\n' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-086', 'baremetal-sdk-original-init-087')
compile(payload, 'original-audit-copy-087-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
