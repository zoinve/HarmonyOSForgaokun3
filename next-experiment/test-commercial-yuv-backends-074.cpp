// Exercises the actual own VDI with explicitly mocked DRM, not GPU evidence.
#include <cassert>
#include <cstdarg>
#include <cstdlib>
#include <dirent.h>
#include <sys/syscall.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <drm_fourcc.h>
#include "allocator-074.cpp"
#include "image-helper-074.h"

enum class Fault074 { None, Create, Prime, ShortSize, Handle };
static Fault074 fault074 = Fault074::None;
static drm_mode_create_dumb created074;
static unsigned destroyed074;

extern "C" int __wrap_ioctl(int, unsigned long command, ...)
{
    va_list args;
    va_start(args, command);
    void *argument = va_arg(args, void *);
    va_end(args);
    if (command == DRM_IOCTL_MODE_CREATE_DUMB) {
        if (fault074 == Fault074::Create) { errno = ENOMEM; return -1; }
        auto &request = *static_cast<drm_mode_create_dumb *>(argument);
        request.pitch = ((request.width * (request.bpp / 8)) + 63) & ~63U;
        request.size = (uint64_t(request.pitch) * request.height + 4095) & ~UINT64_C(4095);
        if (fault074 == Fault074::ShortSize) request.size = 1;
        request.handle = 1;
        created074 = request;
        return 0;
    }
    if (command == DRM_IOCTL_MODE_DESTROY_DUMB) { ++destroyed074; return 0; }
    if (command == DMA_BUF_IOCTL_SYNC) return 0;
    errno = EINVAL;
    return -1;
}

extern "C" int AuroraOpenDisplayDrm(AuroraDrmDisplay *display, int)
{
    display->fd = open("/dev/null", O_RDWR | O_CLOEXEC);
    return display->fd < 0 ? -1 : 0;
}

extern "C" int drmPrimeHandleToFD(int, uint32_t, uint32_t, int *fd)
{
    if (fault074 == Fault074::Prime) return -1;
    *fd = static_cast<int>(syscall(SYS_memfd_create, "own-layout-fixture", 1));
    assert(*fd >= 0 && !ftruncate(*fd, created074.size));
    return 0;
}

extern "C" BufferHandle *AllocateBufferHandle(uint32_t fds, uint32_t ints)
{
    if (fault074 == Fault074::Handle) return nullptr;
    auto *handle = static_cast<BufferHandle *>(calloc(1, sizeof(BufferHandle) + 4 * (fds + ints)));
    assert(handle);
    handle->fd = -1;
    handle->reserveFds = fds;
    handle->reserveInts = ints;
    return handle;
}

extern "C" void FreeBufferHandle(BufferHandle *handle)
{
    if (handle->fd >= 0) close(handle->fd);
    free(handle);
}

static unsigned fd_count074()
{
    DIR *directory = opendir("/proc/self/fd");
    assert(directory);
    unsigned count = 0;
    while (readdir(directory)) ++count;
    closedir(directory);
    return count;
}

int main()
{
    unsigned before = fd_count074();
    auto *vdi = CreateDisplayBufferVdi();
    assert(vdi);
    const int formats074[] = {PIXEL_FMT_RGBA_8888, PIXEL_FMT_RGBX_8888,
                       PIXEL_FMT_BGRA_8888, PIXEL_FMT_BGRX_8888,
                       PIXEL_FMT_YCBCR_420_SP, PIXEL_FMT_YCRCB_420_SP,
                       commercial074::BLOB_FORMAT};
    for (int format : formats074) {
        const bool yuv074 = commercial074::yuv(format);
        const bool blob074 = commercial074::blob(format);
        BufferAllocInfo info{};
        info.width = blob074 ? 262160 : 2160;
        info.height = blob074 ? 1 : 1440;
        info.format = format;
        info.usage = blob074 ? 0x2b : 0x40b;
        BufferHandle *handle = nullptr;
        assert(!vdi->AllocMem(info, handle) && handle);
        assert(created074.bpp == (yuv074 || blob074 ? 8 : 32));
        assert(created074.height == (yuv074 ? 2160 : info.height));
        assert(!vdi->RegisterBuffer(*handle));
        auto *address = static_cast<unsigned char *>(vdi->Mmap(*handle));
        assert(address && handle->virAddr == address);
        address[0] = 17;
        address[handle->size - 1] = 29;
        assert(vdi->Mmap(*handle) == address);
        assert(!vdi->Unmap(*handle) && handle->virAddr == address);
        assert(!vdi->Unmap(*handle) && !handle->virAddr);
        OHOS::HDI::Display::Buffer::V1_2::ImageLayout image;
        assert(!vdi->GetImageLayout(*handle, image));
        assert(image.planes.size() == (yuv074 ? 2 : 1));
        assert(image.planes[0].hStride == uint32_t(handle->stride));
        assert(image.planes[0].vStride == (yuv074 || blob074 ? 1 : 4));
        if (yuv074) {
            assert(image.planes[1].offset == uint32_t(handle->stride * handle->height));
            assert(image.planes[1].hStride == uint32_t(handle->stride));
            assert(image.planes[1].vStride == 2);
        }
        EGLint attributes[19];
        assert(image_attributes074(handle, attributes) == !blob074);
        if (!blob074) {
            assert(attributes[11] == handle->stride);
            assert(attributes[yuv074 ? 18 : 12] == EGL_NONE);
            if (yuv074) {
                assert(attributes[5] == static_cast<EGLint>(format == PIXEL_FMT_YCBCR_420_SP ? DRM_FORMAT_NV12 : DRM_FORMAT_NV21));
                assert(attributes[13] == handle->fd);
                assert(attributes[15] == handle->stride * handle->height);
                assert(attributes[17] == handle->stride);
            }
        }
        // A forged short backing is rejected before either mmap or import.
        assert(!ftruncate(handle->fd, 1));
        assert(vdi->RegisterBuffer(*handle) != 0);
        assert(!vdi->Mmap(*handle));
        assert(!image_attributes074(handle, attributes));
        vdi->FreeMem(*handle);
        for (auto fault : {Fault074::Create, Fault074::Prime, Fault074::ShortSize, Fault074::Handle}) {
            fault074 = fault;
            handle = reinterpret_cast<BufferHandle *>(1);
            assert(vdi->AllocMem(info, handle) != 0 && !handle);
        }
        fault074 = Fault074::None;
        info.usage |= HBM_USE_PROTECTED;
        assert(vdi->AllocMem(info, handle) == NOT_SUPPORT && !handle);
        info.usage = 0x40b;
        info.expectedSize = UINT32_MAX;
        assert(vdi->AllocMem(info, handle) == NOT_SUPPORT && !handle);
    }
    DestroyDisplayBufferVdi(vdi);
    assert(destroyed074 == 35);
    assert(fd_count074() == before);
    return 0;
}
