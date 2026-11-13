"""Reversible load witness and data-directory trace; no EGL state consumption."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-graphics-egl-trace-001.py')))
OLD = parent['HELPER']
NEW = OLD.replace('/run/graphics-trace', '/data/graphics-trace')
NEW = NEW.replace('        if (fd >= 0) {', '''        if (fd < 0 && !strcmp(name, "bridge_loaded")) {
            int failure = errno;
            int n = snprintf(line, sizeof(line), "EGL_TRACE_OPEN_FAILED pid=%ld errno=%d\\n", (long)getpid(), failure);
            if (n > 0 && n < (int)sizeof(line)) (void)write(2, line, (size_t)n);
        }
        if (fd >= 0) {''')
NEW = NEW.replace('}\n// END GRAPHICS_TRACE_001', '''__attribute__((constructor)) void graphics_trace_loaded() {
    graphics_trace("bridge_loaded", trace_value(getuid()));
}
}
// END GRAPHICS_TRACE_001''')


def adapt(source):
    traced = parent['adapt'](source)
    assert traced.count(OLD) == 1
    return traced.replace(OLD, NEW, 1)


def strip_trace(source):
    assert source.count(NEW) == 1
    return parent['strip_trace'](source.replace(NEW, OLD, 1))
