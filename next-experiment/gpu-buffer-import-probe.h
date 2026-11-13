/* Throwaway independent buffer import comparison; no service buffer changes. */
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <xf86drm.h>
#include <drm_mode.h>
#include <gbm.h>

static void gpu902_import(void *lib, EGLDisplay display, const char *kind,
                          int fd, int width, int height, int pitch)
{
    PFNEGLCREATEIMAGEKHRPROC create = (PFNEGLCREATEIMAGEKHRPROC)dlsym(lib, "eglCreateImageKHR");
    PFNEGLDESTROYIMAGEKHRPROC destroy = (PFNEGLDESTROYIMAGEKHRPROC)dlsym(lib, "eglDestroyImageKHR");
    __typeof__(&eglGetError) error = (__typeof__(&eglGetError))dlsym(lib, "eglGetError");
    if (!create || !destroy || !error || fd < 0) {
        printf("GPU902_IMPORT kind=%s skipped=1 fd=%d errno=%d\n", kind, fd, errno);
        return;
    }
    EGLint attributes[] = {EGL_WIDTH, width, EGL_HEIGHT, height,
        EGL_LINUX_DRM_FOURCC_EXT, GBM_FORMAT_ABGR8888,
        EGL_DMA_BUF_PLANE0_FD_EXT, fd, EGL_DMA_BUF_PLANE0_OFFSET_EXT, 0,
        EGL_DMA_BUF_PLANE0_PITCH_EXT, pitch, EGL_NONE};
    (void)error();
    EGLImageKHR image = create(display, EGL_NO_CONTEXT, EGL_LINUX_DMA_BUF_EXT, NULL, attributes);
    EGLint result = error();
    printf("GPU902_IMPORT kind=%s image=%p error=%x fd=%d pitch=%d\n",
           kind, image, result, fd, pitch);
    if (image != EGL_NO_IMAGE_KHR) destroy(display, image);
}

static void gpu902_buffers(void *lib, EGLDisplay display)
{
    void *heap = dlopen("/vendor/lib64/l410-graphics/allocator/libdmabufheap.z.so", RTLD_NOW | RTLD_LOCAL);
    if (heap) {
        int (*open_heap)(const char *) = (int (*)(const char *))dlsym(heap, "DmabufHeapOpen");
        int (*allocate)(int, void *) = (int (*)(int, void *))dlsym(heap, "DmabufHeapBufferAlloc");
        int (*close_heap)(int) = (int (*)(int))dlsym(heap, "DmabufHeapClose");
        struct { int fd; int pad; uint64_t size; uint32_t flags; uint32_t align; } request = {-1, 0, 4096, 0, 0};
        int h = open_heap ? open_heap("system") : -1;
        int rc = h >= 0 && allocate ? allocate(h, &request) : -1;
        printf("GPU902_HEAP handle=%d rc=%d fd=%d errno=%d\n", h, rc, request.fd, errno);
        if (!rc) { gpu902_import(lib, display, "original-ion", request.fd, 16, 16, 64); close(request.fd); }
        if (h >= 0 && close_heap) close_heap(h);
        dlclose(heap);
    } else printf("GPU902_HEAP load_error=%s\n", dlerror());
    int card = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
    struct drm_mode_create_dumb dumb = {.width = 16, .height = 16, .bpp = 32};
    int rc = card >= 0 ? ioctl(card, DRM_IOCTL_MODE_CREATE_DUMB, &dumb) : -1;
    printf("GPU902_DUMB fd=%d rc=%d errno=%d\n", card, rc, errno);
    if (!rc) {
        int prime = -1;
        if (!drmPrimeHandleToFD(card, dumb.handle, DRM_CLOEXEC | DRM_RDWR, &prime)) {
            gpu902_import(lib, display, "drm-dumb", prime, 16, 16, dumb.pitch); close(prime);
        }
        struct drm_mode_destroy_dumb destroy = {.handle = dumb.handle};
        (void)ioctl(card, DRM_IOCTL_MODE_DESTROY_DUMB, &destroy);
    }
    struct gbm_device *device = card >= 0 ? gbm_create_device(card) : NULL;
    if (device) {
        unsigned usage[] = {GBM_BO_USE_RENDERING | GBM_BO_USE_LINEAR, GBM_BO_USE_RENDERING};
        const char *names[] = {"gbm-linear", "gbm-rendering"};
        for (unsigned i = 0; i < 2; ++i) {
            struct gbm_bo *bo = gbm_bo_create(device, 16, 16, GBM_FORMAT_ABGR8888, usage[i]);
            printf("GPU902_GBM kind=%s bo=%p errno=%d\n", names[i], (void *)bo, errno);
            if (!bo) continue;
            int prime = gbm_bo_get_fd(bo);
            gpu902_import(lib, display, names[i], prime, 16, 16, gbm_bo_get_stride(bo));
            if (prime >= 0) close(prime);
            gbm_bo_destroy(bo);
        }
        gbm_device_destroy(device);
    }
    if (card >= 0) close(card);
    puts("GPU902_BUFFER_COMPARISON_DONE desktop_not_tested=1");
}
