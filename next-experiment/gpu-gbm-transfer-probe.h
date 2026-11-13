/* Independent buffers only: exercise Mesa's CPU-to-VirGL transfer path. */
static int gpu904_gbm()
{
    AuroraDrmDisplay drm = {};
    require(!AuroraOpenDisplayDrm(&drm, 0), "GBM DRM enumerate");
    gbm_device *device = gbm_create_device(drm.fd); require(device, "GBM device");
    auto platform = reinterpret_cast<PFNEGLGETPLATFORMDISPLAYEXTPROC>(eglGetProcAddress("eglGetPlatformDisplayEXT"));
    require(platform, "GBM EGL platform");
    EGLDisplay display = platform(EGL_PLATFORM_GBM_KHR, device, nullptr);
    require(eglInitialize(display, nullptr, nullptr), "GBM EGL initialize");
    EGLint attrs[] = {EGL_SURFACE_TYPE, 0, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT, EGL_NONE};
    EGLConfig config; EGLint count = 0;
    require(eglChooseConfig(display, attrs, &config, 1, &count) && count, "GBM EGL config");
    EGLint ca[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
    EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, ca);
    require(context && eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, context), "GBM EGL current");
    const char *renderer = reinterpret_cast<const char *>(glGetString(GL_RENDERER));
    require(renderer && strstr(renderer, "virgl"), "GBM hardware renderer");
    auto create_image = reinterpret_cast<PFNEGLCREATEIMAGEKHRPROC>(eglGetProcAddress("eglCreateImageKHR"));
    auto destroy_image = reinterpret_cast<PFNEGLDESTROYIMAGEKHRPROC>(eglGetProcAddress("eglDestroyImageKHR"));
    auto target = reinterpret_cast<PFNGLEGLIMAGETARGETTEXTURE2DOESPROC>(eglGetProcAddress("glEGLImageTargetTexture2DOES"));
    require(create_image && destroy_image && target, "GBM image entries");
    for (unsigned sample = 0; sample < 2; ++sample) {
        unsigned w = sample ? 1920 : 13, h = sample ? 1080 : 7;
        gbm_bo *bo = gbm_bo_create(device, w, h, GBM_FORMAT_ABGR8888, GBM_BO_USE_RENDERING | GBM_BO_USE_LINEAR);
        require(bo, "GBM BO allocation");
        uint32_t stride = 0; void *mapping = nullptr;
        auto pixels = static_cast<unsigned char *>(gbm_bo_map(bo, 0, 0, w, h, GBM_BO_TRANSFER_WRITE, &stride, &mapping));
        require(pixels && stride >= w * 4, "GBM CPU map");
        for (unsigned y = 0; y < h; ++y) for (unsigned x = 0; x < w; ++x) {
            unsigned char *p = pixels + y * stride + x * 4;
            p[0] = 64; p[1] = 128; p[2] = 191; p[3] = 255;
        }
        gbm_bo_unmap(bo, mapping);
        int fd = gbm_bo_get_fd(bo); require(fd >= 0, "GBM export");
        EGLint ia[] = {EGL_WIDTH, static_cast<EGLint>(w), EGL_HEIGHT, static_cast<EGLint>(h),
            EGL_LINUX_DRM_FOURCC_EXT, DRM_FORMAT_ABGR8888, EGL_DMA_BUF_PLANE0_FD_EXT, fd,
            EGL_DMA_BUF_PLANE0_OFFSET_EXT, 0, EGL_DMA_BUF_PLANE0_PITCH_EXT, static_cast<EGLint>(gbm_bo_get_stride(bo)), EGL_NONE};
        EGLImageKHR image = create_image(display, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, nullptr, ia);
        printf("GPU904_IMPORT sample=%u size=%ux%u cpu_stride=%u exported_stride=%u image=%p error=%x\n",
            sample, w, h, stride, gbm_bo_get_stride(bo), image, eglGetError());
        require(image != EGL_NO_IMAGE_KHR, "GBM image import");
        GLuint texture, fbo; glGenTextures(1, &texture); glBindTexture(GL_TEXTURE_2D, texture);
        target(GL_TEXTURE_2D, image); glGenFramebuffers(1, &fbo); glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
        require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "GBM imported FBO");
        unsigned char pixel[4] = {}; glReadPixels(0, 0, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
        printf("GPU904_PIXEL sample=%u rgba=%u,%u,%u,%u\n", sample, pixel[0], pixel[1], pixel[2], pixel[3]);
        require(glGetError() == GL_NO_ERROR && pixel[0] == 64 && pixel[1] == 128 && pixel[2] == 191 && pixel[3] == 255, "GBM pixel content");
        glBindFramebuffer(GL_FRAMEBUFFER, 0); glDeleteFramebuffers(1, &fbo); glDeleteTextures(1, &texture);
        destroy_image(display, image); close(fd); gbm_bo_destroy(bo);
    }
    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
    eglDestroyContext(display, context); eglTerminate(display); gbm_device_destroy(device); close(drm.fd);
    puts("GPU904_PASS gbm_cpu_write_gpu_readback no_kms_changes=1 desktop_not_tested=1");
    return 0;
}
