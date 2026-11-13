"""Reversible logging at real display-creation boundaries; no fallback changes."""
from pathlib import Path
import runpy

parent = runpy.run_path(str(Path(__file__).with_name('original-graphics-egl-trace-003.py')))
CHANGES = [
    ('    if (AuroraOpenDisplayDrm(&display.drm, 0)) {',
     '    int drm_result = AuroraOpenDisplayDrm(&display.drm, 0);\n'
     '    graphics_trace("drm_open_result", trace_value(drm_result));\n'
     '    if (drm_result) {'),
    ('    display.device = gbm_create_device(display.drm.fd);',
     '    display.device = gbm_create_device(display.drm.fd);\n'
     '    graphics_trace("gbm_device", trace_value(display.device));'),
    ('    display.egl = fn(EGL_PLATFORM_GBM_KHR, display.device, nullptr);',
     '    display.egl = fn(EGL_PLATFORM_GBM_KHR, display.device, nullptr);\n'
     '    graphics_trace("mesa_display", trace_value(display.egl));'),
]


def adapt(source):
    traced = parent['adapt'](source)
    for old, new in CHANGES:
        assert traced.count(old) == 1
        traced = traced.replace(old, new, 1)
    return traced


def strip_trace(source):
    for old, new in reversed(CHANGES):
        assert source.count(new) == 1
        source = source.replace(new, old, 1)
    return parent['strip_trace'](source)
