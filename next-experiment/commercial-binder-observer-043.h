// Public Binder UAPI observation. Original buffers and security decisions are untouched.
#include <linux/android/binder.h>
#include <sys/ioctl.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>

struct BinderSnapshot043 {
    uint32_t handle, code, flags;
    uint64_t bytes, objects, end;
    unsigned interface;
};

static unsigned interface043(const void *buffer, size_t size)
{
    if (!buffer || size < 12) return 0;
    const auto *data = static_cast<const unsigned char *>(buffer);
    uint32_t policy, length;
    memcpy(&policy, data, 4);
    memcpy(&length, data + 8, 4);
    if (policy != 0x100 || length > 64 || size < 12 + (size_t(length) + 1) * 2) return 0;
    const char *names[] = {"ohos.rosen.RenderServiceConnection", "ohos.rosen.RenderService"};
    for (unsigned n = 0; n < 2; ++n) {
        if (strlen(names[n]) != length) continue;
        bool equal = true;
        for (size_t i = 0; i < length; ++i)
            if (data[12 + i * 2] != static_cast<unsigned char>(names[n][i]) || data[13 + i * 2]) equal = false;
        if (equal && !data[12 + length * 2] && !data[13 + length * 2]) return n + 1;
    }
    return 0;
}

static unsigned snapshots043(const binder_write_read &request, BinderSnapshot043 *out, unsigned capacity)
{
    if (!request.write_buffer || request.write_size > 65536 || request.write_consumed > request.write_size) return 0;
    const auto *data = reinterpret_cast<const unsigned char *>(request.write_buffer);
    size_t offset = 0;
    unsigned found = 0, commands = 0;
    while (offset + 4 <= request.write_size && commands++ < 256) {
        uint32_t command;
        memcpy(&command, data + offset, 4);
        offset += 4;
        size_t bytes = _IOC_SIZE(command);
        if (_IOC_TYPE(command) != 'c' || bytes > request.write_size - offset) break;
        if ((command == BC_TRANSACTION || command == BC_TRANSACTION_SG) &&
            bytes >= sizeof(binder_transaction_data) && offset + bytes > request.write_consumed) {
            binder_transaction_data transaction;
            memcpy(&transaction, data + offset, sizeof(transaction));
            unsigned type = interface043(reinterpret_cast<const void *>(transaction.data.ptr.buffer), transaction.data_size);
            if (type && found < capacity)
                out[found++] = {transaction.target.handle, transaction.code, transaction.flags,
                               transaction.data_size, transaction.offsets_size, offset + bytes, type};
        }
        offset += bytes;
    }
    return found;
}

#ifndef BINDER_OBSERVER043_TEST
static void binder_record043(const BinderSnapshot043 &entry, int fd, unsigned long serial,
                             bool returned, int result, int error, uint64_t consumed)
{
    int saved = errno;
    struct timespec stamp = {};
    clock_gettime(CLOCK_MONOTONIC, &stamp);
    uint64_t now = uint64_t(stamp.tv_sec) * 1000000 + stamp.tv_nsec / 1000;
    unsigned group = entry.code == 0 ? 0 : (entry.code == 17 ? 1 : 2);
    unsigned slot = (entry.interface - 1) * 6 + group * 2 + unsigned(returned);
    static unsigned initial[12] = {}, late[12] = {};
    static uint64_t previous[12] = {};
    bool emit = __atomic_add_fetch(&initial[slot], 1u, __ATOMIC_RELAXED) <= 6;
    if (!emit && now >= 70000000 && __atomic_load_n(&late[slot], __ATOMIC_RELAXED) < 16) {
        uint64_t old = __atomic_load_n(&previous[slot], __ATOMIC_RELAXED);
        if (now - old >= 5000000 && __atomic_compare_exchange_n(&previous[slot], &old, now, false, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) {
            __atomic_add_fetch(&late[slot], 1u, __ATOMIC_RELAXED);
            emit = true;
        }
    }
    if (emit) {
        char path[64], target[128] = {};
        snprintf(path, sizeof(path), "/proc/self/fd/%d", fd);
        ssize_t length = readlink(path, target, sizeof(target) - 1);
        if (length < 0) strcpy(target, "unavailable");
        using Print = int(*)(int, int, unsigned, const char *, const char *, ...);
        static auto print = reinterpret_cast<Print>(dlsym(RTLD_DEFAULT, "HiLogPrint"));
        if (print) print(3, 4, 0x0D002511, "CommercialIPC043",
            "IPC043 phase=%{public}s pid=%{public}d uid=%{public}d fd=%{public}d device=%{public}s serial=%{public}lu interface=%{public}u handle=%{public}u code=%{public}u flags=%{public}u bytes=%{public}llu objects=%{public}llu result=%{public}d errno=%{public}d consumed=%{public}llu end=%{public}llu mono_us=%{public}llu",
            returned ? "return" : "enter", getpid(), getuid(), fd, target, serial, entry.interface,
            entry.handle, entry.code, entry.flags, (unsigned long long)entry.bytes,
            (unsigned long long)entry.objects, result, error, (unsigned long long)consumed,
            (unsigned long long)entry.end, (unsigned long long)now);
    }
    errno = saved;
}

extern "C" int ioctl(int fd, int command, ...)
{
    int saved = errno;
    va_list args;
    va_start(args, command);
    void *argument = va_arg(args, void *);
    va_end(args);
    using Original = int(*)(int, int, ...);
    static auto original = reinterpret_cast<Original>(dlsym(RTLD_NEXT, "ioctl"));
    if (!original) abort();
    static thread_local bool active = false;
    if (active || uint32_t(command) != uint32_t(BINDER_WRITE_READ) || !argument) {
        errno = saved;
        return original(fd, command, argument);
    }
    active = true;
    const auto *request = static_cast<const binder_write_read *>(argument);
    BinderSnapshot043 records[16] = {};
    unsigned count = snapshots043(*request, records, 16);
    static unsigned long serials = 0;
    unsigned long serial = __atomic_add_fetch(&serials, 1ul, __ATOMIC_RELAXED);
    for (unsigned i = 0; i < count; ++i) binder_record043(records[i], fd, serial, false, 0, 0, request->write_consumed);
    errno = saved;
    int result = original(fd, command, argument);
    int error = errno;
    for (unsigned i = 0; i < count; ++i) binder_record043(records[i], fd, serial, true, result, error, request->write_consumed);
    active = false;
    errno = error;
    return result;
}
#endif
