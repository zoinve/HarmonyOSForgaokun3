"""Keep repeated symbol lookups from exhausting actual EGL result tracing."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-graphics-egl-trace-002.py')))
OLD = parent['NEW']
anchor = '    static std::atomic<unsigned> count{0};'
assert OLD.count(anchor) == 1
NEW = OLD.replace(anchor, '''    static std::atomic<bool> mesa_logged{false};
    if (!strcmp(name, "mesa_library") && mesa_logged.exchange(true, std::memory_order_relaxed)) {
        errno = saved;
        return;
    }
''' + anchor)


def adapt(source):
    traced = parent['adapt'](source)
    assert traced.count(OLD) == 1
    return traced.replace(OLD, NEW, 1)


def strip_trace(source):
    assert source.count(NEW) == 1
    return parent['strip_trace'](source.replace(NEW, OLD, 1))
