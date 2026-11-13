// PRIVATE pinned layout witnesses, not official headers or a replacement HDI.
#define _GNU_SOURCE 1
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstddef>
#include <dlfcn.h>
#include <fcntl.h>
#include <unistd.h>

struct Packer { uint64_t capacity, cursor, start; uint32_t length, pad; uint64_t slot; void *data; };
struct Unpacker { uint64_t capacity, cursor, start; uint32_t length, pad; const void *data; };
struct Entry { int32_t number; uint32_t pad; void *object; };
struct Vector { Entry *begin, *end, *capacity; };
static_assert(sizeof(Packer) == 48 && offsetof(Packer, data) == 40);
static_assert(sizeof(Unpacker) == 40 && offsetof(Unpacker, data) == 32);
static_assert(sizeof(Entry) == 16 && offsetof(Entry, object) == 8 && sizeof(Vector) == 24);
static bool live(int fd) { return fcntl(fd, F_GETFD) >= 0; }

int main()
{
    setbuf(stdout, nullptr);
    alarm(20);
    char line[2048] = {};
    FILE *f = fopen("/proc/cmdline", "r");
    if (!f) return 77;
    fread(line, 1, sizeof(line) - 1, f); fclose(f);
    if (!strstr(line, "harmony.smq.fdstream=1") || !access("/dev/dri/card0", F_OK) ||
        !access("/dev/dri/renderD128", F_OK)) return 77;
    void *lib = dlopen("/system/lib64/lab-softpipe-167/libdisplay_composer_service_1.5.z.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib) { printf("FDSTREAM001_FAIL dlopen=%s\n", dlerror()); return 1; }
    Dl_info info = {};
    void *factory = dlsym(lib, "DisplayComposerImplGetInstance"); // Resolve ONLY, never call.
    if (!factory || !dladdr(factory, &info) || !info.dli_fbase) return 2;
    auto *base = static_cast<unsigned char *>(info.dli_fbase);
    const uint32_t pack_head[] = {0xd000004f, 0xf94381ef, 0xca1d01ef, 0xca1e01ef};
    const uint32_t unpack_head[] = {0xd101c3ff, 0xa9017bfd, 0xa9026ffc, 0xa90367fa};
    if (memcmp(base + 0x1ce74, pack_head, sizeof(pack_head)) ||
        memcmp(base + 0x211fc, unpack_head, sizeof(unpack_head))) return 3;
    auto pack = reinterpret_cast<int (*)(int, Packer *, Vector *, bool)>(base + 0x1ce74);
    auto unpack = reinterpret_cast<int (*)(Unpacker *, const Vector *, int *)>(base + 0x211fc);
    auto dec = reinterpret_cast<void (*)(void *, const void *)>(dlsym(lib, "_ZN4OHOS7RefBase12DecStrongRefEPKv"));
    if (!dec) return 4;
    // Pair the ORIGINAL packer's IncStrongRef with ORIGINAL DecStrongRef, using
    // the vtable's actual virtual-base adjustment, exactly as its vector teardown.
    auto clear = [&](Vector &v) {
        for (Entry *e = v.begin; e != v.end; ++e) {
            if (!e->object) continue;
            unsigned char *table = nullptr;
            memcpy(&table, e->object, sizeof(table));
            ptrdiff_t adjustment = 0;
            memcpy(&adjustment, table - 24, sizeof(adjustment));
            dec(static_cast<unsigned char *>(e->object) + adjustment, &e->object);
            e->object = nullptr;
        }
        v.end = v.begin;
    };
    auto check = [](const char *name, bool pass) {
        printf("FDSTREAM001_CASE name=%s pass=%d\n", name, pass);
        if (!pass) _exit(5);
    };
    Entry entry = {};
    Vector vector = {&entry, &entry, &entry + 1}; // One preallocated element; no reallocation.
    int32_t word = 0;
    Packer p = {4, 0, 0, 0, 0, 0, &word};
    int rc = pack(-1, &p, &vector, true), out = -99;
    Unpacker u = {4, 0, 0, 0, 0, &word};
    int urc = unpack(&u, &vector, &out);
    check("negative_roundtrip", rc == 0 && p.cursor == 4 && word == -1 &&
          vector.end == vector.begin && urc == 0 && out == -1 && u.cursor == 4);
    word = 123; u = {4, 0, 0, 0, 0, &word}; out = -99;
    urc = unpack(&u, &vector, &out);
    check("unknown_number_rejected", urc == -1 && out == -1 && u.cursor == 4);
    u = {3, 0, 0, 0, 0, &word}; out = -99;
    urc = unpack(&u, &vector, &out);
    check("truncated_word_preserves_output", urc == -1 && out == -99 && u.cursor == 0);
    int pipefd[2]; if (pipe(pipefd)) return 6;
    word = 0; p = {4, 0, 0, 0, 0, 0, &word};
    rc = pack(pipefd[0], &p, &vector, true);
    check("duplicate_pack_number_matches", rc == 0 && p.cursor == 4 && vector.end == &entry + 1 &&
          word >= 0 && word == entry.number && entry.object && live(pipefd[0]));
    u = {4, 0, 0, 0, 0, &word}; out = -99;
    urc = unpack(&u, &vector, &out);
    check("duplicate_unpack_distinct_live_fd", urc == 0 && out >= 0 && out != pipefd[0] && live(out));
    const int moved = out;
    u = {4, 0, 0, 0, 0, &word}; out = -99;
    urc = unpack(&u, &vector, &out);
    check("repeated_unpack_alias_not_new_fd", urc == 0 && out == moved && live(moved));
    clear(vector);
    const char sent = 'F'; char received = 0;
    const bool data_ok = write(pipefd[1], &sent, 1) == 1 && read(moved, &received, 1) == 1;
    check("vector_release_preserves_moved_pipe", live(moved) && live(pipefd[0]) && data_ok && received == sent);
    close(moved);
    word = 0; p = {4, 0, 0, 0, 0, 0, &word};
    rc = pack(pipefd[0], &p, &vector, false);
    u = {4, 0, 0, 0, 0, &word}; out = -99;
    urc = unpack(&u, &vector, &out);
    clear(vector);
    check("nonduplicating_path_returns_caller_fd", rc == 0 && urc == 0 && out == pipefd[0] && live(pipefd[0]));
    close(pipefd[0]); close(pipefd[1]);
    puts("FDSTREAM001_PASS cases=8 original_code=1 factory_called=0 smq_not_tested=1 desktop_not_tested=1");
    return 0;
}
