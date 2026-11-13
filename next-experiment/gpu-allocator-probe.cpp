/* Throwaway: compare only independently allocated buffers; never set KMS state. */
#include "idisplay_buffer_vdi.h"
#include "aurora_drm.h"
#include "display_type.h"
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl3.h>
#include <GLES2/gl2ext.h>
#include <drm_fourcc.h>
#include <gbm.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <dlfcn.h>
#include <unistd.h>

using Interface = OHOS::HDI::Display::Buffer::V1_0::IDisplayBufferVdi;
static void require(bool ok, const char *step)
{
    if (!ok) { printf("GPU903_FAIL step=%s egl=%x\n", step, eglGetError()); std::exit(2); }
}
int main(int argc, char **argv)
{
    setbuf(stdout, nullptr); alarm(30);
    if (argc != 2) return 1;
    printf("GPU903_BEGIN allocator=%s own_buffers_only=1\n", argv[1]);
    void *lib = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!lib) { printf("GPU903_LOAD_ERROR %s\n", dlerror()); return 2; }
    auto create = reinterpret_cast<Interface *(*)()>(dlsym(lib, "CreateDisplayBufferVdi"));
    auto destroy = reinterpret_cast<void (*)(Interface *)>(dlsym(lib, "DestroyDisplayBufferVdi"));
    require(create && destroy, "factory symbols");
    Interface *allocator = create(); require(allocator, "factory");
    AuroraDrmDisplay drm = {}; require(!AuroraOpenDisplayDrm(&drm, 0), "DRM enumerate");
    gbm_device *device = gbm_create_device(drm.fd); require(device, "GBM device");
    auto platform = reinterpret_cast<PFNEGLGETPLATFORMDISPLAYEXTPROC>(eglGetProcAddress("eglGetPlatformDisplayEXT"));
    require(platform, "platform entry");
    EGLDisplay display = platform(EGL_PLATFORM_GBM_KHR, device, nullptr);
    require(eglInitialize(display, nullptr, nullptr), "initialize");
    EGLint attrs[] = {EGL_SURFACE_TYPE, 0, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT, EGL_NONE};
    EGLConfig config; EGLint count = 0;
    require(eglChooseConfig(display, attrs, &config, 1, &count) && count, "config");
    EGLint ctxattrs[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
    EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, ctxattrs);
    require(context != EGL_NO_CONTEXT && eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, context), "current");
    const char *renderer = reinterpret_cast<const char *>(glGetString(GL_RENDERER));
    require(renderer && strstr(renderer, "virgl"), "hardware renderer");
    printf("GPU903_RENDERER %s\n", renderer);
    auto image_create = reinterpret_cast<PFNEGLCREATEIMAGEKHRPROC>(eglGetProcAddress("eglCreateImageKHR"));
    auto image_destroy = reinterpret_cast<PFNEGLDESTROYIMAGEKHRPROC>(eglGetProcAddress("eglDestroyImageKHR"));
    auto image_target = reinterpret_cast<PFNGLEGLIMAGETARGETTEXTURE2DOESPROC>(eglGetProcAddress("glEGLImageTargetTexture2DOES"));
    require(image_create && image_destroy && image_target, "image entry points");
    int result = 0;
    for (int sample = 0; sample < 2; ++sample) {
        OHOS::HDI::Display::Buffer::V1_0::AllocInfo info = {
            sample ? 1920U : 13U, sample ? 1080U : 7U,
            HBM_USE_CPU_READ | HBM_USE_CPU_WRITE | HBM_USE_HW_RENDER,
            PIXEL_FMT_RGBA_8888, 0};
        BufferHandle *handle = nullptr;
        int rc = allocator->AllocMem(info, handle);
        printf("GPU903_ALLOC rc=%d handle=%p\n", rc, static_cast<void *>(handle));
        require(!rc && handle, "allocate");
        require(handle->width == static_cast<int>(info.width) && handle->height == static_cast<int>(info.height), "geometry");
        auto pixels = static_cast<unsigned char *>(allocator->Mmap(*handle));
        require(pixels && handle->stride >= handle->width * 4, "map");
        for (int y = 0; y < handle->height; ++y) for (int x = 0; x < handle->width; ++x) {
            unsigned char *p = pixels + y * handle->stride + x * 4;
            p[0] = 64; p[1] = 128; p[2] = 191; p[3] = 255;
        }
        require(!allocator->FlushCache(*handle), "flush");
        require(!allocator->Unmap(*handle), "unmap");
        EGLint ia[] = {EGL_WIDTH, handle->width, EGL_HEIGHT, handle->height,
            EGL_LINUX_DRM_FOURCC_EXT, DRM_FORMAT_ABGR8888,
            EGL_DMA_BUF_PLANE0_FD_EXT, handle->fd, EGL_DMA_BUF_PLANE0_OFFSET_EXT, 0,
            EGL_DMA_BUF_PLANE0_PITCH_EXT, handle->stride, EGL_NONE};
        EGLImageKHR image = image_create(display, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, nullptr, ia);
        printf("GPU903_IMPORT sample=%d fd=%d size=%dx%d stride=%d image=%p error=%x\n", sample,
            handle->fd, handle->width, handle->height, handle->stride, image, eglGetError());
        if (image == EGL_NO_IMAGE_KHR) { allocator->FreeMem(*handle); result = 4; break; }
        GLuint texture, fbo; glGenTextures(1, &texture); glBindTexture(GL_TEXTURE_2D, texture);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        image_target(GL_TEXTURE_2D, image); glGenFramebuffers(1, &fbo);
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
        require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "imported FBO");
        unsigned char pixel[4] = {}; glReadPixels(0, 0, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
        printf("GPU903_PIXEL sample=%d rgba=%u,%u,%u,%u\n", sample, pixel[0], pixel[1], pixel[2], pixel[3]);
        require(glGetError() == GL_NO_ERROR && pixel[0] == 64 && pixel[1] == 128 && pixel[2] == 191 && pixel[3] == 255, "pixel content");
        glBindFramebuffer(GL_FRAMEBUFFER, 0); glDeleteFramebuffers(1, &fbo); glDeleteTextures(1, &texture);
        image_destroy(display, image); allocator->FreeMem(*handle);
    }
    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
    eglDestroyContext(display, context); eglTerminate(display); gbm_device_destroy(device); close(drm.fd);
    destroy(allocator); dlclose(lib);
    if (!result) puts("GPU903_PASS allocator_import_pixels no_kms_changes=1 desktop_not_tested=1");
    return result;
}
