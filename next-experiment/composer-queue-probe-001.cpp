// PRIVATE pinned original-binary characterization, not a public HDI ABI.
#define _GNU_SOURCE 1
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <unistd.h>

int main()
{
    setbuf(stdout, nullptr);
    alarm(20);
    char line[2048] = {};
    FILE *f = fopen("/proc/cmdline", "r");
    if (!f) return 77;
    fread(line, 1, sizeof(line) - 1, f); fclose(f);
    if (!strstr(line, "harmony.smq.queue=1") || !access("/dev/dri/card0", F_OK) ||
        !access("/dev/dri/renderD128", F_OK)) return 77;
    void *lib = dlopen("/system/lib64/lab-softpipe-167/libdisplay_composer_service_1.5.z.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib) { printf("QUEUE001_FAIL dlopen=%s\n", dlerror()); return 1; }
    Dl_info info = {};
    void *factory = dlsym(lib, "DisplayComposerImplGetInstance"); // Resolve ONLY.
    if (!factory || !dladdr(factory, &info) || !info.dli_fbase) return 2;
    auto *base = static_cast<unsigned char *>(info.dli_fbase);
    const uint32_t ctor_head[] = {0xa9bd7bfd, 0xa90157f6, 0xa9024ff4, 0x910003fd};
    const uint32_t dtor_head[] = {0xa9be7bfd, 0xa9014ff4, 0x910003fd, 0xaa0003f3};
    const uint32_t rw_head[] = {0xd10183ff, 0xa9017bfd, 0xa90267fa, 0xa9035ff8};
    if (memcmp(base + 0x1a110, ctor_head, sizeof(ctor_head)) ||
        memcmp(base + 0x1a648, dtor_head, sizeof(dtor_head)) ||
        memcmp(base + 0x1b15c, rw_head, sizeof(rw_head)) ||
        memcmp(base + 0x23144, rw_head, sizeof(rw_head))) return 3;
    auto ctor = reinterpret_cast<void (*)(void *, unsigned, unsigned)>(base + 0x1a110);
    auto dtor = reinterpret_cast<void (*)(void *)>(base + 0x1a648);
    auto get = reinterpret_cast<int (*)(void *, int *, uint64_t)>(base + 0x1b15c);
    auto put = reinterpret_cast<int (*)(void *, const int *, uint64_t)>(base + 0x23144);
    // Original make_shared at 0x19f78 allocates 88 bytes; object at +24 => 64.
    alignas(8) unsigned char queue[64] = {};
    ctor(queue, 8, 1); // Original responder uses SmqType=1 at 0x19f90.
    int status = -99;
    memcpy(&status, queue, sizeof(status));
    if (status != 0) {
        printf("QUEUE001_BLOCKED original_constructor_status=%d ashmem_present=%d\n", status, !access("/dev/ashmem", F_OK));
        dtor(queue);
        return 70; // Preserve real prerequisite failure; no fallback or fake FD.
    }
    auto check = [](const char *name, bool pass) {
        printf("QUEUE001_CASE name=%s pass=%d\n", name, pass);
        if (!pass) _exit(5);
    };
    unsigned char *meta = nullptr;
    memcpy(&meta, queue + 48, sizeof(meta));
    int fd = -1;
    if (meta) memcpy(&fd, meta, sizeof(fd));
    check("original_constructor_and_ashmem", meta && fd >= 0 && fcntl(fd, F_GETFD) >= 0);
    int out[8] = {-99};
    check("empty_read_unchanged", get(queue, out, 1) == -61 && out[0] == -99);
    check("zero_read_rejected", get(queue, out, 0) == -22);
    const int first[] = {0x41, 17, -1};
    const int wrc = put(queue, first, 3), rrc = get(queue, out, 3);
    check("same_process_fifo", wrc == 0 && rrc == 0 && !memcmp(first, out, sizeof(first)));
    const int full[] = {1, 2, 3, 4, 5, 6, 7, 8};
    const int frc = put(queue, full, 8), over = put(queue, full, 1), drain = get(queue, out, 8);
    check("full_rejected_without_corruption", frc == 0 && over == -7 && drain == 0 && !memcmp(full, out, sizeof(full)));
    const int wrap[] = {0x402, 37, 0x41, 99};
    const int ww = put(queue, wrap, 4), wr = get(queue, out, 4);
    check("wrapped_fifo", ww == 0 && wr == 0 && !memcmp(wrap, out, sizeof(wrap)));
    const pid_t child = fork();
    if (child == 0) _exit(put(queue, first, 3) == 0 ? 0 : 9);
    int ws = -1;
    const bool waited = child > 0 && waitpid(child, &ws, 0) == child;
    const int cross = waited ? get(queue, out, 3) : -99;
    check("fork_inherited_shared_queue", waited && WIFEXITED(ws) && WEXITSTATUS(ws) == 0 &&
          cross == 0 && !memcmp(first, out, sizeof(first)));
    dtor(queue);
    check("destructor_closes_backing_fd", fcntl(fd, F_GETFD) == -1);
    puts("QUEUE001_PASS cases=8 original_code=1 factory_called=0 composer_request_not_tested=1 desktop_not_tested=1");
    return 0;
}
