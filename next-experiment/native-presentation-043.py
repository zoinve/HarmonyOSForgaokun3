"""Reversible instrumentation of existing 041; no DRM operation is replaced."""
COMPOSER = [
    ('#include "native-gpu-composer-041.h"', '#include "native-gpu-composer-041.h"\n#include "native-presentation-043.h"'),
    ('void flipped(int, unsigned int, unsigned int, unsigned int, void *)\n{',
     'void flipped(int, unsigned int sequence, unsigned int seconds, unsigned int microseconds, void *)\n{\n    NativePresent043::completed(sequence, seconds, microseconds);'),
    ('    state.saved = drmModeGetCrtc(state.drm.fd, state.drm.crtc);',
     '    { int saved043=errno; uint64_t cap043=0; int rc043=drmGetCap(state.drm.fd,DRM_CAP_TIMESTAMP_MONOTONIC,&cap043);\n      NativePresent043::configure_clock(rc043,cap043); errno=saved043; }\n    state.saved = drmModeGetCrtc(state.drm.fd, state.drm.crtc);'),
    ('    if (drmModePageFlip(state.drm.fd, state.drm.crtc, state.buffers[slot].fb, DRM_MODE_PAGE_FLIP_EVENT, nullptr)) return FAIL;',
     '    NativePresent043::begin("client", state.buffers[slot].fb);\n    int flip043=drmModePageFlip(state.drm.fd, state.drm.crtc, state.buffers[slot].fb, DRM_MODE_PAGE_FLIP_EVENT, nullptr);\n    if(flip043){int saved043=errno; NativePresent043::failed(flip043,saved043); errno=saved043; return FAIL;}'),
    ('    NativeGpu041::shutdown();', '    NativeGpu041::shutdown();\n    NativePresent043::flush();'),
]
CURSOR = [
    ('        if(drmModePageFlip(state.drm.fd,state.drm.crtc,output.fb,DRM_MODE_PAGE_FLIP_EVENT,nullptr))continue;',
     '        NativePresent043::begin("cursor",output.fb);\n        int flip043=drmModePageFlip(state.drm.fd,state.drm.crtc,output.fb,DRM_MODE_PAGE_FLIP_EVENT,nullptr);\n        if(flip043){int saved043=errno; NativePresent043::failed(flip043,saved043); errno=saved043; continue;}'),
]


def change(text, replacements, reverse=False):
    for before, after in reversed(replacements) if reverse else replacements:
        old, new = (after, before) if reverse else (before, after)
        assert text.count(old) == 1, (old, text.count(old))
        text = text.replace(old, new, 1)
    return text


def adapt(composer, cursor):
    return change(composer, COMPOSER), change(cursor, CURSOR)


def strip(composer, cursor):
    return change(composer, COMPOSER, True), change(cursor, CURSOR, True)
