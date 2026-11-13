// Pinned PRIVATE binary characterization, not a replacement HDI implementation.
#define _GNU_SOURCE 1
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <unistd.h>

struct State {
    uint64_t capacity, cursor, section_start;
    uint32_t length, padding;
    const void *data;
};
static_assert(sizeof(State) == 40 && __builtin_offsetof(State, data) == 32);

int main()
{
    setbuf(stdout, nullptr);
    alarm(20);
    char cmdline[2048] = {};
    FILE *f = fopen("/proc/cmdline", "r");
    if (!f) return 77;
    const size_t count = fread(cmdline, 1, sizeof(cmdline) - 1, f);
    fclose(f);
    if (!count || !strstr(cmdline, "harmony.smq.parser=1") ||
        !access("/dev/dri/card0", F_OK) || !access("/dev/dri/renderD128", F_OK)) return 77;
    void *lib = dlopen("/system/lib64/lab-softpipe-167/libdisplay_composer_service_1.5.z.so",
                       RTLD_NOW | RTLD_LOCAL);
    if (!lib) { printf("PARSER001_FAIL dlopen=%s\n", dlerror()); return 1; }
    // Resolve the exported factory ONLY to locate the ELF. Never invoke it.
    void *symbol = dlsym(lib, "DisplayComposerImplGetInstance");
    Dl_info info = {};
    if (!symbol || !dladdr(symbol, &info) || !info.dli_fbase) return 2;
    auto *base = static_cast<const unsigned char *>(info.dli_fbase);
    const uint32_t expected[] = {0xa9be7bfd, 0xf9000bf3, 0x910003fd, 0xa9402007};
    if (memcmp(base + 0x1ac38, expected, sizeof(expected))) return 3;
    using Begin = bool (*)(State *, int &);
    auto begin = reinterpret_cast<Begin>(const_cast<unsigned char *>(base + 0x1ac38));
    struct Case { const char *name; uint64_t capacity; uint32_t magic, length;
                  bool accepted; uint64_t cursor; int command; };
    const Case cases[] = {
        {"valid", 12, 0xb5b5b5b5, 12, true, 12, 0x41},
        {"empty", 0, 0xb5b5b5b5, 12, false, 0, -99},
        {"magic_only", 4, 0xb5b5b5b5, 12, false, 4, -99},
        {"missing_length", 8, 0xb5b5b5b5, 12, false, 8, 0x41},
        {"short_header", 11, 0xb5b5b5b5, 12, false, 8, 0x41},
        {"bad_magic", 12, 0x01020304, 12, false, 4, -99},
        {"zero_length_header_only", 12, 0xb5b5b5b5, 0, true, 12, 0x41},
        {"oversize_length_header_only", 12, 0xb5b5b5b5, 0xffffffff, true, 12, 0x41},
    };
    for (const auto &c : cases) {
        const uint32_t data[] = {c.magic, 0x41, c.length};
        State state = {c.capacity, 0, 0, 0, 0, data};
        int command = -99;
        const bool accepted = begin(&state, command);
        const bool pass = accepted == c.accepted && state.cursor == c.cursor &&
                          command == c.command && (!accepted || state.length == c.length);
        printf("PARSER001_CASE name=%s accepted=%d cursor=%llu command=%d length=%u pass=%d\n",
               c.name, accepted, static_cast<unsigned long long>(state.cursor), command,
               state.length, pass);
        if (!pass) return 4;
    }
    puts("PARSER001_PASS cases=8 original_code=1 factory_called=0 payload_not_parsed=1 smq_not_tested=1 desktop_not_tested=1");
    // Process exit handles library teardown; no service factory or display methods called.
    return 0;
}
