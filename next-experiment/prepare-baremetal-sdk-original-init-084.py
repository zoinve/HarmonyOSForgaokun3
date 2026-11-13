"""Observe genuine profile file events without permission mediation or target writes."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-083.py')))
source = parent['source'].replace('ORIGINAL_INIT083_', 'ORIGINAL_INIT084_').replace('GRAPHICS083_', 'GRAPHICS084_')
source = source.replace('#include <unistd.h>', '#include <unistd.h>\n#include <sys/fanotify.h>\n#include <poll.h>\n#include <time.h>')
helper = r'''
static void graphics_profile_events_084(void)
{
    int fd = fanotify_init(FAN_CLOEXEC | FAN_NONBLOCK, O_RDONLY | O_LARGEFILE | O_CLOEXEC);
    int saved = fd < 0 ? errno : 0;
    dprintf(1, "GRAPHICS084_PROFILE_WATCH_INIT fd=%d errno=%d permission_events=0\n", fd, saved);
    if (fd < 0) return;
    unsigned long long mask = FAN_OPEN | FAN_ACCESS | FAN_CLOSE_NOWRITE | FAN_EVENT_ON_CHILD;
    int rc = fanotify_mark(fd, FAN_MARK_ADD | FAN_MARK_ONLYDIR, mask, AT_FDCWD, "/system/profile");
    dprintf(1, "GRAPHICS084_PROFILE_WATCH_MARK rc=%d errno=%d path=/system/profile\n", rc, rc ? errno : 0);
    if (rc) { close(fd); return; }
    pid_t watcher = fork();
    if (watcher != 0) {
        dprintf(1, "GRAPHICS084_PROFILE_WATCH_FORK pid=%ld errno=%d\n", (long)watcher, watcher < 0 ? errno : 0);
        close(fd);
        return;
    }
    alarm(490);
    struct timespec start, now;
    if (clock_gettime(CLOCK_MONOTONIC, &start)) { close(fd); _exit(74); }
    unsigned count = 0;
    while (count < 2048) {
        if (clock_gettime(CLOCK_MONOTONIC, &now) || now.tv_sec - start.tv_sec >= 480) break;
        struct pollfd pfd = { .fd = fd, .events = POLLIN };
        int ready = poll(&pfd, 1, 1000);
        if (ready < 0 && errno == EINTR) continue;
        if (ready < 0) { dprintf(1, "GRAPHICS084_PROFILE_WATCH_POLL_ERROR errno=%d\n", errno); break; }
        if (!ready) continue;
        char buffer[8192] __attribute__((aligned(8)));
        ssize_t bytes = read(fd, buffer, sizeof(buffer));
        if (bytes < 0 && (errno == EINTR || errno == EAGAIN)) continue;
        if (bytes <= 0) { dprintf(1, "GRAPHICS084_PROFILE_WATCH_READ_ERROR bytes=%ld errno=%d\n", (long)bytes, bytes < 0 ? errno : 0); break; }
        struct fanotify_event_metadata *meta = (struct fanotify_event_metadata *)buffer;
        while (FAN_EVENT_OK(meta, bytes)) {
            if (meta->vers != FANOTIFY_METADATA_VERSION) {
                dprintf(1, "GRAPHICS084_PROFILE_WATCH_VERSION observed=%u\n", meta->vers);
                if (meta->fd >= 0) close(meta->fd);
                close(fd);
                _exit(74);
            }
            if (meta->mask & FAN_Q_OVERFLOW)
                dprintf(1, "GRAPHICS084_PROFILE_WATCH_OVERFLOW actual=1\n");
            if (meta->fd >= 0) {
                char link[64], path[4096];
                snprintf(link, sizeof(link), "/proc/self/fd/%d", meta->fd);
                ssize_t n = readlink(link, path, sizeof(path) - 1);
                int error = n < 0 ? errno : 0;
                if (n >= 0) path[n] = 0;
                else strcpy(path, "<readlink_failed>");
                ++count;
                dprintf(1, "GRAPHICS084_PROFILE_EVENT seq=%u pid=%ld mask=0x%llx path=%s link_errno=%d\n",
                        count, (long)meta->pid, (unsigned long long)meta->mask, path, error);
                close(meta->fd);
            }
            meta = FAN_EVENT_NEXT(meta, bytes);
        }
    }
    dprintf(1, "GRAPHICS084_PROFILE_WATCH_END count=%u bounded=1\n", count);
    close(fd);
    _exit(0);
}

'''
anchor = 'static void guest_permissive_config_047('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + anchor)
anchor = '    pid_t observer = fork();'
assert source.count(anchor) == 1
source = source.replace(anchor, '    graphics_profile_events_084();\n' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-083', 'baremetal-sdk-original-init-084')
compile(payload, 'original-profile-events-084-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'], input=payload,
                                   text=True, timeout=180).returncode)
