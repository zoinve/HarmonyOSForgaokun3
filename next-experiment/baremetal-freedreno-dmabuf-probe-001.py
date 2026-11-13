"""Extend the existing hardware triangle probe with a linear GBM/DMA-BUF round trip."""
from pathlib import Path
import runpy


def build_source():
    base=Path(__file__).resolve().parent
    source=runpy.run_path(str(base/'baremetal-freedreno-probe-001.py'))['build_source']()
    source=source.replace('FREEDRENO001_','DMABUF001_')
    anchor='#include <GLES2/gl2.h>'
    source=source.replace(anchor,anchor+'''
#include <GLES2/gl2ext.h>
#include <gbm.h>
#include <libdrm/drm_fourcc.h>
#include <fcntl.h>
#include <inttypes.h>
#include <unistd.h>
#include "baremetal-freedreno-dmabuf-policy-001.h"
''')
    anchor='    GLuint vertex = shader('
    assert source.count(anchor)==1
    start='''    const char *extensions = eglQueryString(display, EGL_EXTENSIONS);
    require(extensions && strstr(extensions, "EGL_EXT_image_dma_buf_import") &&
            strstr(extensions, "EGL_EXT_image_dma_buf_import_modifiers"), "DMA-BUF EGL extensions");
    PFNEGLCREATEIMAGEKHRPROC create_image = (PFNEGLCREATEIMAGEKHRPROC)eglGetProcAddress("eglCreateImageKHR");
    PFNEGLDESTROYIMAGEKHRPROC destroy_image = (PFNEGLDESTROYIMAGEKHRPROC)eglGetProcAddress("eglDestroyImageKHR");
    PFNGLEGLIMAGETARGETTEXTURE2DOESPROC image_texture =
        (PFNGLEGLIMAGETARGETTEXTURE2DOESPROC)eglGetProcAddress("glEGLImageTargetTexture2DOES");
    require(create_image && destroy_image && image_texture, "DMA-BUF image entry points");
    int render_fd = open("/dev/dri/renderD128", O_RDWR | O_CLOEXEC);
    require(render_fd >= 0, "GBM render fd");
    struct gbm_device *gbm = gbm_create_device(render_fd);
    require(gbm != NULL, "GBM device");
    printf("DMABUF001_GBM backend=%s\\n", gbm_device_get_backend_name(gbm));
    uint64_t linear = DRM_FORMAT_MOD_LINEAR;
    struct gbm_bo *bo = gbm_bo_create_with_modifiers2(gbm, 16, 16, GBM_FORMAT_ARGB8888,
                                                     &linear, 1, GBM_BO_USE_RENDERING);
    require(bo != NULL, "linear GBM allocation");
    int dma_fd = gbm_bo_get_fd_for_plane(bo, 0);
    uint32_t width = gbm_bo_get_width(bo), height = gbm_bo_get_height(bo);
    uint32_t stride = gbm_bo_get_stride_for_plane(bo, 0), offset = gbm_bo_get_offset(bo, 0);
    uint64_t modifier = gbm_bo_get_modifier(bo);
    require(dmabuf_meta_ok(dma_fd, width, height, gbm_bo_get_plane_count(bo), stride, offset, modifier)
            && width == 16 && height == 16 && gbm_bo_get_format(bo) == GBM_FORMAT_ARGB8888,
            "single-plane linear ARGB metadata");
    printf("DMABUF001_EXPORT width=%u height=%u stride=%u offset=%u modifier=0x%" PRIx64 "\\n",
           width, height, stride, offset, modifier);
    EGLint image_attributes[] = {
        EGL_WIDTH, (EGLint)width, EGL_HEIGHT, (EGLint)height,
        EGL_LINUX_DRM_FOURCC_EXT, GBM_FORMAT_ARGB8888,
        EGL_DMA_BUF_PLANE0_FD_EXT, dma_fd,
        EGL_DMA_BUF_PLANE0_OFFSET_EXT, (EGLint)offset,
        EGL_DMA_BUF_PLANE0_PITCH_EXT, (EGLint)stride,
        EGL_DMA_BUF_PLANE0_MODIFIER_LO_EXT, 0, EGL_DMA_BUF_PLANE0_MODIFIER_HI_EXT, 0,
        EGL_NONE};
    EGLImageKHR image = create_image(display, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, NULL, image_attributes);
    require(image != EGL_NO_IMAGE_KHR, "EGL DMA-BUF import");
    GLuint texture, framebuffer;
    glGenTextures(1, &texture); glBindTexture(GL_TEXTURE_2D, texture);
    image_texture(GL_TEXTURE_2D, image);
    glGenFramebuffers(1, &framebuffer); glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    require(glGetError() == GL_NO_ERROR && glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE,
            "imported DMA-BUF framebuffer");
'''
    source=source.replace(anchor,start+anchor)
    anchor='    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);'
    assert source.count(anchor)==1
    end='''    /* Re-import the exported FD through a second independent render-node open. */
    int second_fd = open("/dev/dri/renderD128", O_RDWR | O_CLOEXEC);
    require(second_fd >= 0, "second GBM render fd");
    struct gbm_device *second_gbm = gbm_create_device(second_fd);
    require(second_gbm != NULL, "second GBM device");
    struct gbm_import_fd_modifier_data shared = {
        .width=width, .height=height, .format=GBM_FORMAT_ARGB8888, .num_fds=1,
        .fds={dma_fd}, .strides={(int)stride}, .offsets={(int)offset}, .modifier=modifier};
    struct gbm_bo *imported = gbm_bo_import(second_gbm, GBM_BO_IMPORT_FD_MODIFIER,
                                          &shared, GBM_BO_USE_RENDERING);
    require(imported != NULL, "second-device GBM import");
    uint32_t map_stride = 0; void *map_data = NULL;
    unsigned char *mapping = gbm_bo_map(imported, 0, 0, 16, 16, GBM_BO_TRANSFER_READ,
                                         &map_stride, &map_data);
    require(mapping != NULL && map_stride >= 64, "imported GBM CPU mapping");
    const unsigned char *mc = mapping + 8 * map_stride + 8 * 4;
    const unsigned char *mb = mapping + 8 * map_stride;
    unsigned char mapped_center[4] = {mc[2],mc[1],mc[0],mc[3]};
    unsigned char mapped_corner[4] = {mb[2],mb[1],mb[0],mb[3]};
    printf("DMABUF001_MAPPED center_8_8=%u,%u,%u,%u corner_0_8=%u,%u,%u,%u\\n",
           mapped_center[0],mapped_center[1],mapped_center[2],mapped_center[3],
           mapped_corner[0],mapped_corner[1],mapped_corner[2],mapped_corner[3]);
    require(freedreno_pixels_ok(mapped_center, mapped_corner), "shared-memory GPU pixel coherence");
    gbm_bo_unmap(imported, map_data);
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glDeleteFramebuffers(1, &framebuffer); glDeleteTextures(1, &texture);
    require(destroy_image(display, image), "destroy DMA-BUF image");
    gbm_bo_destroy(imported); gbm_device_destroy(second_gbm); close(second_fd);
    close(dma_fd); gbm_bo_destroy(bo); gbm_device_destroy(gbm); close(render_fd);
'''
    source=source.replace(anchor,end+anchor)
    source=source.replace('PASS shader_triangle_and_readback desktop_not_tested=1',
                          'PASS gbm_dmabuf_egl_and_second_device_readback desktop_not_tested=1')
    return source
