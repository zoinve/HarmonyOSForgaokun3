/* Passive KMS callback journal. Caller serializes it with the original state mutex.
   Submission IDs are NOT visual-content IDs. Initial modesets are not callbacks. */
#pragma once
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

namespace NativePresent043 {
struct Pending {
    uint64_t id = 0, submitted = 0;
    uint32_t fb = 0;
    const char *origin = "none";
    bool active = false, unambiguous = true;
};
static Pending pending;
static uint64_t next_id = 0, completed_count = 0;
static int timestamp_monotonic = -1;
static char buffer[8192];
static size_t used = 0;
static unsigned records = 0, flush_failures = 0;
static bool limit_sent = false;

inline uint64_t now_us()
{
    timespec ts{};
    return clock_gettime(CLOCK_MONOTONIC, &ts) ? 0 :
        static_cast<uint64_t>(ts.tv_sec) * 1000000 + ts.tv_nsec / 1000;
}
inline void flush()
{
    int saved = errno;
    // This is the existing, precreated diagnostic file, not a new writable path.
    // A host-side unit test must never write a pretend device trace.
    if (!used || getuid() != 3036) { used = 0; errno = saved; return; }
    int fd = open("/data/native-perf-023.trace", O_WRONLY | O_APPEND | O_CLOEXEC | O_NOFOLLOW);
    struct stat st{};
    size_t done = 0;
    int error = fd < 0 ? errno : 0;
    if (fd >= 0) {
        if (fstat(fd, &st)) error = errno;
        else if (!S_ISREG(st.st_mode) || st.st_nlink != 1 || (st.st_uid != 0 && st.st_uid != 3036)) error = EINVAL;
        else while (done < used) {
            ssize_t n = write(fd, buffer + done, used - done);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0) { error = n < 0 ? errno : EIO; break; }
            done += static_cast<size_t>(n);
        }
        close(fd);
    }
    if (error && flush_failures++ < 8)
        std::fprintf(stderr, "NATIVE_PRESENT043_LOG_ERROR errno=%d unwritten=%zu\n", error, used - done);
    used = 0;
    errno = saved;
}
inline void append(const char *line, size_t size)
{
    if (size > sizeof(buffer)) return;
    if (used + size > sizeof(buffer)) flush();
    std::memcpy(buffer + used, line, size); used += size;
}
inline void emit(const char *kind, unsigned seq = 0, unsigned sec = 0, unsigned usec = 0,
                 uint64_t callback = 0, int result = 0, int error = 0, bool matched = false)
{
    int saved = errno;
    if (records >= 4096) {
        if (!limit_sent) {
            const char line[] = "NATIVE_PRESENT043 kind=limit records=4096 completeness=0\n";
            append(line, sizeof(line) - 1); limit_sent = true; flush();
        }
        errno = saved; return;
    }
    char line[512];
    int n = std::snprintf(line, sizeof(line),
        "NATIVE_PRESENT043 pid=%ld uid=%u kind=%s origin=%s id=%llu fb=%u submit_us=%llu callback_us=%llu drm_seq=%u drm_sec=%u drm_usec=%u timestamp_monotonic=%d matched=%d result=%d error=%d\n",
        static_cast<long>(getpid()), static_cast<unsigned>(getuid()), kind, pending.origin,
        static_cast<unsigned long long>(pending.id), pending.fb,
        static_cast<unsigned long long>(pending.submitted), static_cast<unsigned long long>(callback),
        seq, sec, usec, timestamp_monotonic, matched ? 1 : 0, result, error);
    if (n > 0 && static_cast<size_t>(n) < sizeof(line)) { append(line, n); ++records; }
    errno = saved;
}
inline void configure_clock(int result, uint64_t value)
{
    int saved = errno;
    timestamp_monotonic = result == 0 && value <= 1 ? static_cast<int>(value) : -1;
    emit("clock", 0, 0, 0, 0, result);
    flush();
    errno = saved;
}
inline void begin(const char *origin, uint32_t fb)
{
    int saved = errno;
    bool clean = !pending.active;
    if (!clean) emit("overlap");
    pending = Pending{++next_id, now_us(), fb, origin, true, clean};
    emit("submit");
    errno = saved;
}
inline void failed(int result, int error)
{
    int saved = errno;
    emit("submit_failed", 0, 0, 0, 0, result, error);
    pending.active = false;
    flush();
    errno = saved;
}
inline void completed(unsigned seq, unsigned sec, unsigned usec)
{
    int saved = errno;
    bool matched = pending.active && pending.unambiguous;
    emit("complete", seq, sec, usec, now_us(), 0, 0, matched);
    if (matched) ++completed_count;
    pending.active = false;
    // Bounded batching reduces synchronous I/O, but a killed process can lose
    // its final incomplete batch. This is diagnostic sampling, not a FPS proof.
    if (!matched || completed_count % 16 == 0) flush();
    errno = saved;
}
} // namespace NativePresent043
