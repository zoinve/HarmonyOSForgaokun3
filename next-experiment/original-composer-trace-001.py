"""Reversible, bounded logging only; original provider operations stay intact."""
import re

HELPER = r'''
// COMPOSER_TRACE_HELPER_BEGIN
#include <atomic>
#include <sys/stat.h>
static void composer_trace(const char *stage)
{
    const int saved = errno;
    static std::atomic<unsigned> count{0};
    if (count.fetch_add(1) < 256) {
        char path[128], line[256];
        snprintf(path, sizeof(path), "/data/graphics-trace/composer-%d.log", getpid());
        int fd = open(path, O_WRONLY | O_CREAT | O_APPEND | O_NOFOLLOW | O_CLOEXEC, 0600);
        if (fd >= 0) {
            struct stat st = {};
            if (!fstat(fd, &st) && S_ISREG(st.st_mode) && st.st_uid == getuid() && st.st_nlink == 1) {
                int n = snprintf(line, sizeof(line), "COMPOSER_TRACE pid=%d uid=%u stage=%s errno=%d\n",
                                 getpid(), static_cast<unsigned>(getuid()), stage, saved);
                if (n > 0 && n < static_cast<int>(sizeof(line))) (void)write(fd, line, n);
            }
            close(fd);
        }
    }
    errno = saved;
}
__attribute__((constructor)) static void composer_trace_loaded() { composer_trace("library_loaded"); }
// COMPOSER_TRACE_HELPER_END
'''


def adapt(source):
    assert 'COMPOSER_TRACE_HELPER_BEGIN' not in source
    anchor = 'using namespace AuroraComposer;'
    assert source.count(anchor) == 1
    traced = source.replace(anchor, HELPER + '\n' + anchor)
    traced, count = re.subn(r'(^API (\w+)\([^\n]*\)\s*\{)',
        lambda m: m[1] + '\n    /*COMPOSER_TRACE*/ composer_trace("entry_' + m[2] + '");', traced, flags=re.M)
    assert count >= 20, count
    for anchor, stage in [
        ('int initialize()\n{', 'initialize_enter'),
        ('    state.saved = drmModeGetCrtc(state.drm.fd, state.drm.crtc);', 'drm_open_success'),
        ('    return OK;\nfail:', 'initialize_success'),
        ('fail:\n', 'initialize_failure'),
        ('    callback(0, true, data);', 'hotplug_before_callback'),
        ('    fprintf(stderr, "AURORA_COMPOSER_HOTPLUG_SENT', 'hotplug_callback_returned'),
    ]:
        assert traced.count(anchor) == 1, anchor
        log = '    /*COMPOSER_TRACE*/ composer_trace("' + stage + '");\n'
        if stage in ('initialize_enter', 'initialize_failure'):
            traced = traced.replace(anchor, anchor + '\n' + log)
        else:
            traced = traced.replace(anchor, log + anchor)
    assert strip_trace(traced) == source
    return traced


def strip_trace(source):
    source = source.replace(HELPER + '\n', '')
    source = re.sub(r'\n    /\*COMPOSER_TRACE\*/ composer_trace\("entry_\w+"\);', '', source)
    source = re.sub(r'    /\*COMPOSER_TRACE\*/ composer_trace\("[a-z_]+"\);\n', '', source)
    # The inserted newline after initialize's brace and the fail label is separate.
    source = source.replace('int initialize()\n{\n\n', 'int initialize()\n{\n')
    source = source.replace('fail:\n\n', 'fail:\n')
    return source
