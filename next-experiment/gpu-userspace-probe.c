/* Throwaway, diskless OHOS EGL/GLES smoke test; not desktop evidence. */
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void require(int ok, const char *step)
{
    if (!ok) {
        printf("GPU883_FAIL step=%s egl=0x%x gl=0x%x\n", step, eglGetError(), glGetError());
        exit(1);
    }
}

static GLuint shader(GLenum kind, const char *source)
{
    GLuint s = glCreateShader(kind);
    glShaderSource(s, 1, &source, NULL);
    glCompileShader(s);
    GLint ok = 0;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[2048];
        glGetShaderInfoLog(s, sizeof(log), NULL, log);
        printf("GPU883_SHADER_LOG %s\n", log);
    }
    require(ok, "compile shader");
    return s;
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    PFNEGLQUERYDEVICESEXTPROC query = (PFNEGLQUERYDEVICESEXTPROC)eglGetProcAddress("eglQueryDevicesEXT");
    PFNEGLGETPLATFORMDISPLAYEXTPROC platform = (PFNEGLGETPLATFORMDISPLAYEXTPROC)eglGetProcAddress("eglGetPlatformDisplayEXT");
    require(query && platform, "device extensions");
    EGLDeviceEXT devices[8];
    EGLint count = 0;
    require(query(8, devices, &count) && count > 0, "enumerate devices");
    EGLDisplay display = platform(EGL_PLATFORM_DEVICE_EXT, devices[0], NULL);
    EGLint major, minor;
    require(eglInitialize(display, &major, &minor), "initialize");
    printf("GPU883_EGL version=%d.%d vendor=%s\n", major, minor, eglQueryString(display, EGL_VENDOR));
    EGLint attributes[] = {EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
                          EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_ALPHA_SIZE, 8, EGL_NONE};
    EGLConfig config;
    require(eglChooseConfig(display, attributes, &config, 1, &count) && count == 1, "choose config");
    require(eglBindAPI(EGL_OPENGL_ES_API), "bind GLES");
    EGLint context_attributes[] = {EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE};
    EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, context_attributes);
    require(context != EGL_NO_CONTEXT, "create context");
    EGLint surface_attributes[] = {EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE};
    EGLSurface surface = eglCreatePbufferSurface(display, config, surface_attributes);
    require(surface != EGL_NO_SURFACE, "pbuffer");
    require(eglMakeCurrent(display, surface, surface, context), "make current");
    const char *renderer = (const char *)glGetString(GL_RENDERER);
    printf("GPU883_GL renderer=%s version=%s\n", renderer ? renderer : "NULL", glGetString(GL_VERSION));
    require(renderer && strstr(renderer, "virgl") && !strstr(renderer, "llvmpipe") && !strstr(renderer, "softpipe"), "hardware VirGL renderer");
    GLuint vertex = shader(GL_VERTEX_SHADER, "attribute vec2 p; void main(){gl_Position=vec4(p,0.0,1.0);}");
    GLuint fragment = shader(GL_FRAGMENT_SHADER, "precision mediump float; void main(){gl_FragColor=vec4(1.0,0.0,0.0,1.0);}");
    GLuint program = glCreateProgram();
    glAttachShader(program, vertex);
    glAttachShader(program, fragment);
    glBindAttribLocation(program, 0, "p");
    glLinkProgram(program);
    GLint linked = 0;
    glGetProgramiv(program, GL_LINK_STATUS, &linked);
    require(linked, "link program");
    glUseProgram(program);
    const GLfloat points[] = {-1.f, -1.f, 1.f, -1.f, 0.f, 1.f};
    glViewport(0, 0, 16, 16);
    glClearColor(0.f, 0.f, 1.f, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, points);
    glEnableVertexAttribArray(0);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    glFinish();
    unsigned char center[4] = {0}, corner[4] = {0};
    glReadPixels(8, 8, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, center);
    glReadPixels(0, 15, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, corner);
    require(glGetError() == GL_NO_ERROR, "draw and readback");
    printf("GPU883_PIXELS center=%u,%u,%u,%u corner=%u,%u,%u,%u\n", center[0], center[1], center[2], center[3], corner[0], corner[1], corner[2], corner[3]);
    require(center[0] > 240 && center[1] < 16 && center[2] < 16 && corner[0] < 16 && corner[2] > 240, "triangle pixels");
    eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
    eglDestroySurface(display, surface);
    eglDestroyContext(display, context);
    eglTerminate(display);
    puts("GPU883_PASS shader_triangle_and_readback desktop_not_tested=1");
    return 0;
}
