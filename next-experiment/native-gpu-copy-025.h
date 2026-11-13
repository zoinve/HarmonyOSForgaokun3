// Included inside the pinned bridge namespace. No CPU pixel mapping or readback.
static bool copy_frame_gpu_025(Window &window,BufferHandle &buffer,int &release_fence)
{
    PerfScope023 timing("egl_gpu_submit_025");
    release_fence=-1;
    const char *version=reinterpret_cast<const char *>(glGetString(GL_VERSION));
    if(!version || !strstr(version,"OpenGL ES 3."))return false;
    auto create=real<PFNEGLCREATEIMAGEKHRPROC>("eglCreateImageKHR");
    auto destroy=real<PFNEGLDESTROYIMAGEKHRPROC>("eglDestroyImageKHR");
    auto target=real<PFNGLEGLIMAGETARGETRENDERBUFFERSTORAGEOESPROC>("glEGLImageTargetRenderbufferStorageOES");
    if(!create || !destroy || !target)return false;
    uint32_t format=buffer.format==PIXEL_FMT_RGBA_8888?DRM_FORMAT_ABGR8888:
        buffer.format==PIXEL_FMT_RGBX_8888?DRM_FORMAT_XBGR8888:
        buffer.format==PIXEL_FMT_BGRA_8888?DRM_FORMAT_ARGB8888:DRM_FORMAT_XRGB8888;
    EGLint attributes[]={EGL_WIDTH,buffer.width,EGL_HEIGHT,buffer.height,
        EGL_LINUX_DRM_FOURCC_EXT,EGLint(format),EGL_DMA_BUF_PLANE0_FD_EXT,buffer.fd,
        EGL_DMA_BUF_PLANE0_OFFSET_EXT,0,EGL_DMA_BUF_PLANE0_PITCH_EXT,buffer.stride,EGL_NONE};
    auto image=create(window.display,EGL_NO_CONTEXT,EGL_LINUX_DMA_BUF_EXT,nullptr,attributes);
    if(image==EGL_NO_IMAGE_KHR){perf_record_023("egl_gpu_import_failed_025",perf_now_023());return false;}
    GLint saved_read=0,saved_draw=0,saved_rb=0,saved_default_read=0;
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&saved_read);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&saved_draw);
    glGetIntegerv(GL_RENDERBUFFER_BINDING,&saved_rb);
    GLboolean scissor=glIsEnabled(GL_SCISSOR_TEST);
    GLuint rb=0,fbo=0;glGenRenderbuffers(1,&rb);glGenFramebuffers(1,&fbo);
    bool success=false;
    if(rb && fbo){
        glBindRenderbuffer(GL_RENDERBUFFER,rb);target(GL_RENDERBUFFER,reinterpret_cast<GLeglImageOES>(image));
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER,fbo);
        glFramebufferRenderbuffer(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_RENDERBUFFER,rb);
        if(glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE){
            glBindFramebuffer(GL_READ_FRAMEBUFFER,0);
            glGetIntegerv(GL_READ_BUFFER,&saved_default_read);glReadBuffer(GL_BACK);
            glDisable(GL_SCISSOR_TEST);
            // Preserve the old bridge's bottom-up GL -> top-down queue orientation.
            glBlitFramebuffer(0,0,window.width,window.height,0,buffer.height,buffer.width,0,GL_COLOR_BUFFER_BIT,GL_NEAREST);
            glReadBuffer(saved_default_read);
            auto create_sync=real<PFNEGLCREATESYNCKHRPROC>("eglCreateSyncKHR");
            auto duplicate=real<PFNEGLDUPNATIVEFENCEFDANDROIDPROC>("eglDupNativeFenceFDANDROID");
            auto destroy_sync=real<PFNEGLDESTROYSYNCKHRPROC>("eglDestroySyncKHR");
            if(create_sync && duplicate && destroy_sync){
                auto sync=create_sync(window.display,EGL_SYNC_NATIVE_FENCE_ANDROID,nullptr);
                if(sync!=EGL_NO_SYNC_KHR){glFlush();release_fence=duplicate(window.display,sync);destroy_sync(window.display,sync);}
            }
            if(release_fence<0){
                // Correctness fallback, explicitly measured; never report it as asynchronous.
                auto start=perf_now_023();glFinish();perf_record_023("egl_gpu_sync_fallback_025",start);
            }else perf_record_023("egl_gpu_native_fence_025",perf_now_023());
            success=true;
        }else perf_record_023("egl_gpu_fbo_failed_025",perf_now_023());
    }
    if(scissor)glEnable(GL_SCISSOR_TEST);else glDisable(GL_SCISSOR_TEST);
    glBindFramebuffer(GL_READ_FRAMEBUFFER,GLuint(saved_read));
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER,GLuint(saved_draw));
    glBindRenderbuffer(GL_RENDERBUFFER,GLuint(saved_rb));
    if(fbo)glDeleteFramebuffers(1,&fbo);if(rb)glDeleteRenderbuffers(1,&rb);
    destroy(window.display,image);
    return success;
}
