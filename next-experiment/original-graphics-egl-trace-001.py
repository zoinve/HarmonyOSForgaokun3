"""Reversible diagnostics on a COPY of the bridge; never consume EGL errors."""
HELPER = r'''
// BEGIN GRAPHICS_TRACE_001
#include <atomic>
#include <fcntl.h>
#include <sys/stat.h>
#include <cstdint>
#include <type_traits>
namespace {
template<class T> uintptr_t trace_value(T value) {
    if constexpr (std::is_pointer<T>::value) return reinterpret_cast<uintptr_t>(value);
    else return static_cast<uintptr_t>(value);
}
void graphics_trace(const char *name, uintptr_t value) {
    int saved = errno;
    static std::atomic<unsigned> count{0};
    if (count.fetch_add(1, std::memory_order_relaxed) < 256) {
        char path[96], line[192];
        snprintf(path, sizeof(path), "/run/graphics-trace/egl-%ld.log", (long)getpid());
        int fd = open(path, O_WRONLY | O_APPEND | O_CREAT | O_NOFOLLOW | O_CLOEXEC, 0600);
        if (fd >= 0) {
            struct stat st{};
            if (!fstat(fd, &st) && S_ISREG(st.st_mode) && st.st_uid == getuid() && st.st_nlink == 1) {
                int n = snprintf(line, sizeof(line), "EGL_TRACE pid=%ld name=%s value=0x%lx errno=%d\n",
                                 (long)getpid(), name, (unsigned long)value, saved);
                if (n > 0 && n < (int)sizeof(line)) (void)write(fd, line, (size_t)n);
            }
            close(fd);
        }
    }
    errno = saved;
}
}
// END GRAPHICS_TRACE_001
'''

REPLACEMENTS = [
    ('    return library;\n}', '    graphics_trace("mesa_library", trace_value(library));\n    return library;\n}'),
    ('    return reinterpret_cast<T>(symbol);',
     '    if (!symbol) graphics_trace(name, 0);\n    return reinterpret_cast<T>(symbol);'),
    ('EGLBoolean error(EGLint code) { local_error = code; return EGL_FALSE; }',
     'EGLBoolean error(EGLint code) { graphics_trace("bridge_error", trace_value(code)); local_error = code; return EGL_FALSE; }'),
    ('extern "C" ret name signature { auto fn = real<decltype(&name)>(#name); return fn ? fn arguments : fallback; }',
     'extern "C" ret name signature { auto fn = real<decltype(&name)>(#name); auto result = fn ? fn arguments : fallback; graphics_trace(#name, trace_value(result)); return result; }'),
]


def adapt(source):
    assert 'GRAPHICS_TRACE_001' not in source
    for old, new in REPLACEMENTS:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    anchor = '\nnamespace {'
    assert anchor in source
    return source.replace(anchor, HELPER + anchor, 1)


def strip_trace(source):
    assert source.count(HELPER) == 1
    source = source.replace(HELPER, '', 1)
    for old, new in reversed(REPLACEMENTS):
        assert source.count(new) == 1
        source = source.replace(new, old)
    return source
