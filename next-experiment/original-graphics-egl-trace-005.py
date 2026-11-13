"""Failure-only loader diagnostics; no retry, backend load or EGL error read."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-graphics-egl-trace-004.py')))
HELPER = r'''
namespace {
void graphics_trace_text(const char *name, const char *message) {
    int saved = errno;
    static std::atomic<unsigned> count{0};
    if (count.fetch_add(1, std::memory_order_relaxed) < 16) {
        char path[96], line[768], clean[512];
        size_t i = 0;
        for (; message && message[i] && i < sizeof(clean) - 1; ++i)
            clean[i] = (message[i] == '\n' || message[i] == '\r') ? ' ' : message[i];
        clean[i] = 0;
        snprintf(path, sizeof(path), "/data/graphics-trace/egl-%ld.log", (long)getpid());
        int fd = open(path, O_WRONLY | O_APPEND | O_CREAT | O_NOFOLLOW | O_CLOEXEC, 0600);
        if (fd >= 0) {
            struct stat st{};
            if (!fstat(fd, &st) && S_ISREG(st.st_mode) && st.st_uid == getuid() && st.st_nlink == 1) {
                int n = snprintf(line, sizeof(line), "EGL_TRACE_TEXT pid=%ld name=%s text=%s\n",
                                 (long)getpid(), name, clean);
                if (n > 0 && n < (int)sizeof(line)) (void)write(fd, line, (size_t)n);
            }
            close(fd);
        }
    }
    errno = saved;
}
}
'''
OLD = '    graphics_trace("gbm_device", trace_value(display.device));'
NEW = OLD + r'''
    if (!display.device) {
        int saved = errno;
        const char *loader_error = dlerror();
        graphics_trace_text("gbm_loader_error", loader_error ? loader_error : "<none>");
        Dl_info info{};
        if (dladdr(reinterpret_cast<void *>(&gbm_create_device), &info))
            graphics_trace_text("gbm_implementation", info.dli_fname);
        graphics_trace("gbm_backend_access", trace_value(access("/system/lib64/lab-virgl883/gbm/dri_gbm.so", R_OK)));
        errno = saved;
    }'''


def adapt(source):
    traced = parent['adapt'](source)
    anchor = '\n// END GRAPHICS_TRACE_001'
    assert traced.count(anchor) == 1 and traced.count(OLD) == 1
    return traced.replace(anchor, HELPER + anchor, 1).replace(OLD, NEW, 1)


def strip_trace(source):
    assert source.count(NEW) == 1 and source.count(HELPER) == 1
    source = source.replace(NEW, OLD, 1).replace(HELPER, '', 1)
    return parent['strip_trace'](source)
