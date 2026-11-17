/* Target-only snapshot of the stopped namespace's genuine RAM data disk. */
#include <sys/statfs.h>

struct oobe_snapshot121_context { int data; };

static int oobe_sparse_copy121(int source, int destination, off_t length)
{
    unsigned char buffer[1024 * 1024];
    static const unsigned char zero[sizeof(buffer)];
    off_t cursor = 0;
    while (cursor < length) {
        off_t data = lseek(source, cursor, SEEK_DATA);
        if (data < 0) return errno == ENXIO ? ftruncate(destination, length) : -1;
        off_t hole = lseek(source, data, SEEK_HOLE);
        if (hole < data || hole > length || data >= length) return -1;
        for (off_t at = data; at < hole;) {
            size_t wanted = (size_t)(hole - at);
            if (wanted > sizeof(buffer)) wanted = sizeof(buffer);
            ssize_t count = pread(source, buffer, wanted, at);
            if (count < 0 && errno == EINTR) continue;
            if (count <= 0) return -1;
            if (memcmp(buffer, zero, (size_t)count)) {
                ssize_t written = 0;
                while (written < count) {
                    ssize_t n = pwrite(destination, buffer + written,
                                       (size_t)(count - written), at + written);
                    if (n < 0 && errno == EINTR) continue;
                    if (n <= 0) return -1;
                    written += n;
                }
            }
            at += count;
        }
        cursor = hole;
    }
    return ftruncate(destination, length);
}

static void oobe_snapshot121_worker(void *argument)
{
    struct oobe_snapshot121_context *context = argument;
    struct stat state;
    struct statfs filesystem;
    if (fstat(context->data, &state) || state.st_dev != makedev(7, 3) ||
        fstatfs(context->data, &filesystem) || filesystem.f_type != 0xef53)
        _exit(126);
    /* The outer parent has reaped namespace PID 1, which terminates its children. */
    if (syncfs(context->data) || ioctl(context->data, FIFREEZE, 0)) _exit(126);
    if (mkdir("/mnt/lab/private-oobe121", 0700)) _exit(126);
    int directory121 = open("/mnt/lab/private-oobe121", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (directory121 < 0 || fchmod(directory121, 0700)) _exit(126);
    int source121 = open("/native-target/scratch-data.ext4", O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (source121 < 0 || fstat(source121, &state) || !S_ISREG(state.st_mode) ||
        state.st_size != 8589934592LL) _exit(126);
    int output121 = openat(directory121, "data.ext4.partial", O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC, 0600);
    if (output121 < 0 || oobe_sparse_copy121(source121, output121, state.st_size) ||
        fsync(output121) || close(output121) || close(source121)) _exit(126);
    /* linkat refuses to replace a preexisting completed snapshot. */
    if (linkat(directory121, "data.ext4.partial", directory121, "data.ext4", 0) ||
        unlinkat(directory121, "data.ext4.partial", 0) || fsync(directory121)) _exit(126);
    close(directory121);
    dprintf(1, "OOBE121_DATA_SNAPSHOT complete=1 bytes=8589934592 target_private_only=1 settings_modified=0\n");
}

static void oobe_thaw121_worker(void *argument)
{
    struct oobe_snapshot121_context *context = argument;
    if (ioctl(context->data, FITHAW, 0) && errno != EINVAL) _exit(126);
}

static void oobe_snapshot121(int data)
{
    struct oobe_snapshot121_context context = {data};
    int status = commercial_bounded010(oobe_snapshot121_worker, &context, 20000);
    int thaw = commercial_bounded010(oobe_thaw121_worker, &context, 3000);
    dprintf(1, "OOBE121_CAPTURE_RESULT status=%d thaw=%d private_path=/mnt/lab/private-oobe121/data.ext4\n", status, thaw);
    close(data);
}
