/* Throwaway full-product EGL context diagnostic, not desktop evidence. */
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>

#define EGL_LOAD(name) __typeof__(&name) p_##name = (__typeof__(&name))dlsym(lib, #name); if (!p_##name) return 3
#define GL_LOAD(name) __typeof__(&name) p_##name = (__typeof__(&name))p_eglGetProcAddress(#name); if (!p_##name) return 7
int main(int argc, char **argv)
{
    setbuf(stdout, NULL);
    const char *path = argc > 1 ? argv[1] : "/system/lib64/libEGL.so";
    void *lib = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    printf("GPU887_LOAD path=%s handle=%p error=%s\n", path, lib, lib ? "none" : dlerror());
    if (!lib) return 2;
    EGL_LOAD(eglGetDisplay); EGL_LOAD(eglInitialize); EGL_LOAD(eglGetError);
    EGL_LOAD(eglChooseConfig); EGL_LOAD(eglBindAPI); EGL_LOAD(eglCreateContext);
    EGL_LOAD(eglMakeCurrent); EGL_LOAD(eglGetProcAddress);
    EGLDisplay display = p_eglGetDisplay(EGL_DEFAULT_DISPLAY);
    EGLint major = 0, minor = 0;
    EGLBoolean ok = p_eglInitialize(display, &major, &minor);
    printf("GPU887_INITIALIZE ok=%u version=%d.%d error=%x\n", ok, major, minor, p_eglGetError());
    if (!ok) return 4;
    EGLint attributes[] = {EGL_SURFACE_TYPE, EGL_WINDOW_BIT, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
        EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_ALPHA_SIZE, 8, EGL_NONE};
    EGLConfig config; EGLint count = 0;
    ok = p_eglChooseConfig(display, attributes, &config, 1, &count);
    printf("GPU887_CONFIG window=%u count=%d error=%x\n", ok, count, p_eglGetError());
    if (!ok || !count) return 5;
    EGLint recordable[] = {EGL_SURFACE_TYPE, EGL_WINDOW_BIT, 0x3142, EGL_TRUE, EGL_NONE};
    EGLint records = 0; EGLConfig diagnostic;
    ok = p_eglChooseConfig(display, recordable, &diagnostic, 1, &records);
    printf("GPU887_CONFIG recordable=%u count=%d error=%x\n", ok, records, p_eglGetError());
    if (!p_eglBindAPI(EGL_OPENGL_ES_API)) return 6;
    EGLint context_attributes[] = {EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE};
    EGLContext context = p_eglCreateContext(display, config, EGL_NO_CONTEXT, context_attributes);
    printf("GPU887_CONTEXT handle=%p error=%x\n", context, p_eglGetError());
    if (context == EGL_NO_CONTEXT) return 6;
    ok = p_eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, context);
    printf("GPU887_CURRENT ok=%u error=%x\n", ok, p_eglGetError());
    if (!ok) return 6;
    GL_LOAD(glGetString); GL_LOAD(glGenTextures); GL_LOAD(glBindTexture); GL_LOAD(glTexImage2D);
    GL_LOAD(glGenFramebuffers); GL_LOAD(glBindFramebuffer); GL_LOAD(glFramebufferTexture2D);
    GL_LOAD(glCheckFramebufferStatus); GL_LOAD(glClearColor); GL_LOAD(glClear);
    GL_LOAD(glReadPixels); GL_LOAD(glFinish); GL_LOAD(glGetError);
    const char *renderer = (const char *)p_glGetString(GL_RENDERER);
    printf("GPU887_RENDERER %s\n", renderer ? renderer : "NULL");
    if (!renderer || !strstr(renderer, "virgl")) return 8;
    GLuint texture = 0, framebuffer = 0;
    p_glGenTextures(1, &texture); p_glBindTexture(GL_TEXTURE_2D, texture);
    p_glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 16, 16, 0, GL_RGBA, GL_UNSIGNED_BYTE, NULL);
    p_glGenFramebuffers(1, &framebuffer); p_glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    p_glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    if (p_glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) return 9;
    p_glClearColor(0, 1, 0, 1); p_glClear(GL_COLOR_BUFFER_BIT); p_glFinish();
    unsigned char pixel[4] = {0};
    p_glReadPixels(8, 8, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
    GLenum error = p_glGetError();
    printf("GPU887_PIXEL %u,%u,%u,%u error=%x\n", pixel[0], pixel[1], pixel[2], pixel[3], error);
    if (error || pixel[0] || pixel[1] != 255 || pixel[2] || pixel[3] != 255) return 10;
    puts("GPU887_PASS product_frontend_context_readback desktop_not_tested=1");
    return 0;
}
