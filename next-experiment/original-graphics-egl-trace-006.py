"""Observe the actual Mesa make-current result; preserve reference behavior."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-graphics-egl-trace-005.py')))
OLD = '    if (!fn(egl, backing(draw), backing(read), context)) return EGL_FALSE;'
NEW = '''    const EGLBoolean make_current_result = fn(egl, backing(draw), backing(read), context);
    graphics_trace("eglMakeCurrent", static_cast<uintptr_t>(make_current_result));
    if (!make_current_result) return EGL_FALSE;'''

def adapt(source):
    traced = parent['adapt'](source)
    assert traced.count(OLD) == 1
    return traced.replace(OLD, NEW)

def strip_trace(source):
    assert source.count(NEW) == 1
    return parent['strip_trace'](source.replace(NEW, OLD))
