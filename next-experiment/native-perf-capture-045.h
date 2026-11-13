/* Read-only incremental file reader. No process control or hardware operations. */
#ifndef NATIVE_PERF_CAPTURE_045_H
#define NATIVE_PERF_CAPTURE_045_H
#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

struct capture045_result {
    ssize_t read_bytes;
    size_t complete, partial;
    off_t next;
    int error;
};

static struct capture045_result capture045_read(int fd, off_t offset, char *buffer, size_t capacity)
{
    int saved = errno;
    struct capture045_result r = {0, 0, 0, offset, 0};
    _Static_assert(sizeof(off_t) >= 8, "64-bit diagnostic file offsets");
    if (!capacity || capacity > 65536 || offset < 0) {
        r.read_bytes = -1; r.error = EINVAL;
    } else {
        do { r.read_bytes = pread(fd, buffer, capacity, offset); }
        while (r.read_bytes < 0 && errno == EINTR);
        if (r.read_bytes < 0) r.error = errno;
        else {
            r.complete = (size_t)r.read_bytes;
            while (r.complete && buffer[r.complete - 1] != '\n') --r.complete;
            r.partial = (size_t)r.read_bytes - r.complete;
            r.next = offset + (off_t)r.complete;
            if (!r.complete && (size_t)r.read_bytes == capacity) r.error = EMSGSIZE;
        }
    }
    errno = saved;
    return r;
}
#endif
