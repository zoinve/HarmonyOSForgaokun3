#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <unistd.h>

static int batch(int fd, unsigned key, int value)
{
    struct input_event events[2] = {0};
    events[0].type = EV_KEY;
    events[0].code = key;
    events[0].value = value;
    events[1].type = EV_SYN;
    events[1].code = SYN_REPORT;
    ssize_t count;
    do { count = write(fd, events, sizeof(events)); } while (count < 0 && errno == EINTR);
    return count == (ssize_t)sizeof(events) ? 0 : -1;
}

static int chord(int fd, int delay)
{
    int failed = batch(fd, KEY_LEFTALT, 1);
    if (!failed) {
        if (delay) usleep(40000);
        failed = batch(fd, KEY_F4, 1);
        if (delay) usleep(80000);
    }
    /* Always attempt both releases, even after a rejected or short write. */
    int release_f4 = batch(fd, KEY_F4, 0);
    int release_alt = batch(fd, KEY_LEFTALT, 0);
    return failed || release_f4 || release_alt ? -1 : 0;
}

static int self_test(void)
{
    int pipefd[2];
    if (pipe(pipefd) || chord(pipefd[1], 0)) return 1;
    close(pipefd[1]);
    struct input_event events[9];
    ssize_t size = read(pipefd[0], events, sizeof(events));
    close(pipefd[0]);
    if (size != (ssize_t)(8 * sizeof(events[0]))) return 2;
    unsigned codes[] = {KEY_LEFTALT, KEY_F4, KEY_F4, KEY_LEFTALT};
    int values[] = {1, 1, 0, 0};
    for (unsigned i = 0; i < 4; ++i) {
        if (events[i*2].type != EV_KEY || events[i*2].code != codes[i] ||
            events[i*2].value != values[i] || events[i*2+1].type != EV_SYN ||
            events[i*2+1].code != SYN_REPORT || events[i*2+1].value) return 3;
    }
    int full = open("/dev/full", O_WRONLY | O_CLOEXEC);
    if (full < 0 || chord(full, 0) != -1) return 4;
    close(full);
    puts("NORMAL_CLOSE095_TEST sequence=pass failed_write=pass no_device_access=1");
    return 0;
}

static int bit(const unsigned char *bits, unsigned key)
{
    return !!(bits[key / 8] & (1U << (key % 8)));
}

int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "--self-test")) return self_test();
    if (argc != 2 || strcmp(argv[1], "--send-once")) return 64;
    for (unsigned index = 0; index < 32; ++index) {
        char path[64], name[256] = {0};
        snprintf(path, sizeof(path), "/dev/input/event%u", index);
        int fd = open(path, O_RDWR | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
        if (fd < 0) continue;
        struct stat st;
        unsigned char supported[(KEY_MAX + 8) / 8] = {0};
        unsigned char pressed[sizeof(supported)] = {0};
        if (fstat(fd, &st) || !S_ISCHR(st.st_mode) ||
            ioctl(fd, EVIOCGNAME(sizeof(name) - 1), name) < 0 ||
            strcmp(name, "HID 12d1:10b8 Keyboard") ||
            ioctl(fd, EVIOCGBIT(EV_KEY, sizeof(supported)), supported) < 0 ||
            ioctl(fd, EVIOCGKEY(sizeof(pressed)), pressed) < 0 ||
            !bit(supported, KEY_LEFTALT) || !bit(supported, KEY_F4)) {
            close(fd);
            continue;
        }
        unsigned any_pressed = 0;
        for (unsigned i = 0; i < sizeof(pressed); ++i) any_pressed |= pressed[i];
        if (any_pressed) {
            close(fd);
            puts("NORMAL_CLOSE095_REFUSED physical_key_already_pressed=1");
            return 65;
        }
        int result = chord(fd, 1);
        close(fd);
        printf("NORMAL_CLOSE095_SENT device=%s write_success=%d native_close_not_inferred=1 provisioning_unchanged=1\n", path, !result);
        return result ? 66 : 0;
    }
    puts("NORMAL_CLOSE095_REFUSED verified_keyboard_unavailable=1");
    return 67;
}
