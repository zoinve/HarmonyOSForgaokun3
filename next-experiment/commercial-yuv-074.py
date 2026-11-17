"""Own linear NV12/NV21 allocation and native EGL image import changes."""


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after, 1)


def allocator(source):
    source = replace_once(source, '#include <cerrno>',
                          '#include <cerrno>\n#include "commercial-linear-layout-074.h"')
    source = replace_once(source,
        '''    if (!width || !height || width > 16384 || height > 16384 ||
        static_cast<uint64_t>(width) * height * 4 > 256 * 1024 * 1024) return false;
    if (format != PIXEL_FMT_RGBX_8888 && format != PIXEL_FMT_RGBA_8888 &&
        format != PIXEL_FMT_BGRX_8888 && format != PIXEL_FMT_BGRA_8888) return false;''',
        '''    if (!commercial074::dimensions(width, height, format)) return false;''')
    source = replace_once(source,
        '''    return handle.fd >= 0 && handle.width > 0 && handle.height > 0 &&
        handle.size > 0 && handle.stride >= static_cast<int64_t>(handle.width) * 4 &&
        static_cast<int64_t>(handle.stride) * handle.height <= handle.size;''',
        '''    commercial074::LinearLayout layout074;
    if (handle.fd < 0 || handle.width <= 0 || handle.height <= 0 || handle.size <= 0 ||
        !commercial074::layout(handle.width, handle.height, handle.format,
                               handle.stride, handle.size, layout074)) return false;
    struct stat state074;
    return !fstat(handle.fd, &state074) && state074.st_size >= handle.size;''')
    source = replace_once(source,
        '''        uint32_t allocated_width = info.width;
        if (info.usage & ALIGN_512) allocated_width = (allocated_width + 127) & ~127U;
        struct drm_mode_create_dumb request = {};
        request.width = allocated_width;
        request.height = info.height;
        request.bpp = 32;''',
        '''        commercial074::AllocationShape shape074;
        if (!commercial074::allocation_shape(info.width, info.height, info.format,
                                             info.usage & ALIGN_512, shape074)) return NOT_SUPPORT;
        struct drm_mode_create_dumb request = {};
        request.width = shape074.width;
        request.height = shape074.height;
        request.bpp = shape074.bpp;''')
    source = replace_once(source,
        '''        if (request.size > INT_MAX || request.size < info.expectedSize) {''',
        '''        commercial074::LinearLayout layout074;
        if (request.size > INT_MAX || request.size < info.expectedSize ||
            !commercial074::layout(info.width, info.height, info.format,
                                   request.pitch, request.size, layout074)) {''')
    source = replace_once(source,
        '''        layout.planes = {{0, 4, static_cast<uint32_t>(handle.stride)}};''',
        '''        const uint32_t pitch074 = static_cast<uint32_t>(handle.stride);
        if (commercial074::yuv(handle.format)) {
            commercial074::LinearLayout linear074;
            if (!commercial074::layout(handle.width, handle.height, handle.format,
                                       handle.stride, handle.size, linear074)) return -1;
            layout.planes = {{0, pitch074, 1}, {linear074.chroma_offset, pitch074, 2}};
        } else {
            layout.planes = {{0, pitch074, commercial074::blob(handle.format) ? 1U : 4U}};
        }''')
    return source


IMAGE_HELPER = r'''
static bool image_attributes074(const BufferHandle *handle, EGLint (&attrs)[19])
{
    attrs[0] = EGL_NONE;
    if (!handle || handle->fd < 0 || handle->width <= 0 || handle->height <= 0 ||
        handle->size <= 0 || (handle->usage & HBM_USE_PROTECTED)) return false;
    commercial074::LinearLayout linear074;
    if (!commercial074::layout(handle->width, handle->height, handle->format,
                               handle->stride, handle->size, linear074)) return false;
    struct stat state074;
    if (fstat(handle->fd, &state074) || state074.st_size < handle->size) return false;
    uint32_t format074;
    switch (handle->format) {
    case PIXEL_FMT_RGBA_8888: format074 = DRM_FORMAT_ABGR8888; break;
    case PIXEL_FMT_RGBX_8888: format074 = DRM_FORMAT_XBGR8888; break;
    case PIXEL_FMT_BGRA_8888: format074 = DRM_FORMAT_ARGB8888; break;
    case PIXEL_FMT_BGRX_8888: format074 = DRM_FORMAT_XRGB8888; break;
    case PIXEL_FMT_YCBCR_420_SP: format074 = DRM_FORMAT_NV12; break;
    case PIXEL_FMT_YCRCB_420_SP: format074 = DRM_FORMAT_NV21; break;
    default: return false;
    }
    const EGLint base074[] = {EGL_WIDTH, handle->width, EGL_HEIGHT, handle->height,
        EGL_LINUX_DRM_FOURCC_EXT, static_cast<EGLint>(format074),
        EGL_DMA_BUF_PLANE0_FD_EXT, handle->fd, EGL_DMA_BUF_PLANE0_OFFSET_EXT, 0,
        EGL_DMA_BUF_PLANE0_PITCH_EXT, handle->stride};
    unsigned count074 = 0;
    for (EGLint item074 : base074) attrs[count074++] = item074;
    if (linear074.plane_count == 2) {
        const EGLint chroma074[] = {EGL_DMA_BUF_PLANE1_FD_EXT, handle->fd,
            EGL_DMA_BUF_PLANE1_OFFSET_EXT, static_cast<EGLint>(linear074.chroma_offset),
            EGL_DMA_BUF_PLANE1_PITCH_EXT, handle->stride};
        for (EGLint item074 : chroma074) attrs[count074++] = item074;
    }
    attrs[count074] = EGL_NONE;
    return true;
}
'''


def egl(source):
    source = replace_once(source, '#include <drm_fourcc.h>',
        '#include <drm_fourcc.h>\n#include <sys/stat.h>\n#include "commercial-linear-layout-074.h"')
    anchor = 'extern "C" EGLImageKHR eglCreateImageKHR('
    assert source.count(anchor) == 1
    source = source.replace(anchor, IMAGE_HELPER + '\n' + anchor, 1)
    source = replace_once(source,
        '''    if (!valid(handle)) { error(EGL_BAD_PARAMETER); return EGL_NO_IMAGE_KHR; }
    uint32_t format = handle->format == PIXEL_FMT_RGBA_8888 ? DRM_FORMAT_ABGR8888 :
        handle->format == PIXEL_FMT_RGBX_8888 ? DRM_FORMAT_XBGR8888 :
        handle->format == PIXEL_FMT_BGRA_8888 ? DRM_FORMAT_ARGB8888 : DRM_FORMAT_XRGB8888;
    EGLint attrs[] = {EGL_WIDTH, handle->width, EGL_HEIGHT, handle->height, EGL_LINUX_DRM_FOURCC_EXT, int(format),
        EGL_DMA_BUF_PLANE0_FD_EXT, handle->fd, EGL_DMA_BUF_PLANE0_OFFSET_EXT, 0,
        EGL_DMA_BUF_PLANE0_PITCH_EXT, handle->stride, EGL_NONE};
    return fn(egl, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, nullptr, attrs);''',
        '''    EGLint attrs074[19];
    if (!image_attributes074(handle, attrs074)) { error(EGL_BAD_PARAMETER); return EGL_NO_IMAGE_KHR; }
    return fn(egl, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, nullptr, attrs074);''')
    return source
