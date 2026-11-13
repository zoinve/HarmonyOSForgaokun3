// PRIVATE hash-pinned original SDK object characterization; no public ABI claim.
#define _GNU_SOURCE 1
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <dlfcn.h>
#include <fcntl.h>
#include <new>
#include <unistd.h>

static bool live(int fd) { return fcntl(fd, F_GETFD) >= 0; }
static bool closed(int fd) { errno = 0; return fcntl(fd, F_GETFD) == -1 && errno == EBADF; }

int main()
{
    setbuf(stdout, nullptr);
    alarm(20);
    char line[2048] = {};
    FILE *f = fopen("/proc/cmdline", "r");
    if (!f) return 77;
    fread(line, 1, sizeof(line) - 1, f);
    fclose(f);
    if (!strstr(line, "harmony.smq.fd=1") || !access("/dev/dri/card0", F_OK) ||
        !access("/dev/dri/renderD128", F_OK)) return 77;
    void *lib = dlopen("/system/lib64/lab-softpipe-167/libhdifd_parcelable.z.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib) { printf("FD001_FAIL dlopen=%s\n", dlerror()); return 1; }
    const char *prefix = "_ZN4OHOS3HDI7Display15HdifdParcelable";
    auto sym = [&](const char *suffix) {
        char name[160]; snprintf(name, sizeof(name), "%s%s", prefix, suffix);
        void *p = dlsym(lib, name);
        if (!p) { printf("FD001_FAIL symbol=%s\n", name); _exit(2); }
        return p;
    };
    auto ctor = reinterpret_cast<void (*)(void *)>(sym("C1Ev"));
    auto adopt = reinterpret_cast<void (*)(void *, int)>(sym("C1Ei"));
    auto destroy = reinterpret_cast<void (*)(void *)>(sym("D0Ev"));
    auto init = reinterpret_cast<bool (*)(void *, int)>(sym("4InitEi"));
    auto get = reinterpret_cast<int (*)(void *)>(sym("5GetFdEv"));
    auto move = reinterpret_cast<int (*)(void *)>(sym("4MoveEv"));
    // Original Unmarshalling allocates exactly 32 bytes. Real C1/D0 manage RefBase.
    auto fresh = [&]() { void *o = ::operator new(32); ctor(o); return o; };
    auto check = [](const char *name, bool pass) {
        printf("FD001_CASE name=%s pass=%d\n", name, pass);
        if (!pass) _exit(3);
    };
    void *o = fresh();
    check("default_invalid", get(o) == -1);
    destroy(o);
    int p[2]; if (pipe(p)) return 4;
    o = fresh();
    bool ok = init(o, p[0]);
    int held = get(o);
    check("init_duplicates", ok && held >= 0 && held != p[0] && live(p[0]) && live(held));
    destroy(o);
    check("destructor_closes_duplicate_only", closed(held) && live(p[0]));
    o = fresh();
    if (!init(o, p[0])) return 5;
    held = get(o);
    int moved = move(o), repeated = move(o);
    // Move clears ownership, not the stored number; a second call is not a new FD.
    check("move_repeated_same_number", moved == held && repeated == held && get(o) == held);
    destroy(o);
    check("moved_fd_survives_destructor", live(held) && live(p[0]));
    close(held);
    int owned = dup(p[0]); if (owned < 0) return 6;
    o = ::operator new(32); adopt(o, owned);
    check("constructor_adopts", get(o) == owned && live(owned));
    destroy(o);
    check("adopted_fd_closed", closed(owned) && live(p[0]));
    o = fresh();
    check("negative_init", init(o, -1) && get(o) == -1);
    destroy(o);
    close(p[0]); close(p[1]);
    puts("FD001_PASS cases=8 original_code=1 factory_called=0 smq_not_tested=1 desktop_not_tested=1");
    return 0;
}
