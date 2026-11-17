/* Fixed read-only SSH commands. Never execute commands or emit raw input logs. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#ifndef DIAG_LOG_ROOT
#define DIAG_LOG_ROOT "/logs"
#endif
#ifndef DIAG_FOLLOW_SECONDS
#define DIAG_FOLLOW_SECONDS 30
#endif

static const size_t maximum_read = 2 * 1024 * 1024;

static double monotonic(void)
{
    struct timespec value;
    if (clock_gettime(CLOCK_MONOTONIC, &value)) return -1;
    return value.tv_sec + value.tv_nsec / 1e9;
}

static int log_open(const char *name, struct stat *metadata)
{
    char path[512];
    int count = snprintf(path, sizeof(path), "%s/%s", DIAG_LOG_ROOT, name);
    if (count < 0 || (size_t)count >= sizeof(path)) return -1;
    int fd = open(path, O_RDONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) return -1;
    if (fstat(fd, metadata) || !S_ISREG(metadata->st_mode)) {
        close(fd);
        return -1;
    }
    return fd;
}

static void settings_event(const char *line)
{
    const char *event = NULL;
    if (strstr(line, "hap file verify failed, bundlePath: /system/app/Settings/Settings.hap"))
        event = "settings_install_signature_rejected";
    else if (strstr(line, "bundle not exist -n com.huawei.hmos.settings -u 100 "))
        event = "settings_bundle_absent_user100";
    else if (strstr(line, "StartAbility ability:com.huawei.hmos.settings/"))
        event = "settings_launch_requested";
    if (event) printf("{\"event\":\"%s\"}\n", event);
}

static int settings_read(int follow)
{
    struct stat metadata;
    int fd = log_open("hilog", &metadata);
    if (fd < 0) return 74;
    off_t offset = follow ? metadata.st_size :
        (metadata.st_size > (off_t)maximum_read ? metadata.st_size - (off_t)maximum_read : 0);
    int discard = !follow && offset > 0;
    size_t used = 0, total = 0;
    char block[4096], line[8192];
    double start = monotonic();
    if (start < 0) { close(fd); return 74; }
    if (follow) printf("{\"event\":\"following_settings\",\"maximum_seconds\":%d}\n", DIAG_FOLLOW_SECONDS);
    while (total < maximum_read) {
        ssize_t count = pread(fd, block, sizeof(block), offset);
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) { close(fd); return 74; }
        if (!count) {
            if (!follow) break;
            double now = monotonic();
            if (now < start || now - start >= DIAG_FOLLOW_SECONDS) break;
            struct timespec pause = {0, 100000000};
            nanosleep(&pause, NULL);
            continue;
        }
        offset += count;
        total += (size_t)count;
        for (ssize_t i = 0; i < count; ++i) {
            if (block[i] == '\n') {
                if (!discard) { line[used] = 0; settings_event(line); }
                used = 0;
                discard = 0;
            } else if (!discard) {
                if (!block[i] || used >= sizeof(line) - 1) { discard = 1; used = 0; }
                else line[used++] = block[i];
            }
        }
        double now = monotonic();
        if (now < start || (follow && now - start >= DIAG_FOLLOW_SECONDS)) break;
    }
    close(fd);
    puts("{\"event\":\"settings_read_complete\"}");
    return 0;
}

static int status(void)
{
    const char *names[] = {"hilog", "native", "usb"};
    for (size_t i = 0; i < sizeof(names) / sizeof(names[0]); ++i) {
        struct stat metadata;
        int fd = log_open(names[i], &metadata);
        if (fd < 0) printf("{\"log\":\"%s\",\"available\":false}\n", names[i]);
        else {
            printf("{\"log\":\"%s\",\"available\":true,\"bytes\":%lld}\n", names[i], (long long)metadata.st_size);
            close(fd);
        }
    }
    return 0;
}

int main(int argc, char **argv)
{
    const char *command = getenv("SSH_ORIGINAL_COMMAND");
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (argc != 3 || strcmp(argv[1], "-c") || strcmp(argv[2], "read-only") || !command)
        return 77;
    if (!strcmp(command, "status")) return status();
    if (!strcmp(command, "settings")) return settings_read(0);
    if (!strcmp(command, "follow-settings")) return settings_read(1);
    fputs("{\"error\":\"command_refused\"}\n", stderr);
    return 77;
}
