"""Adapt a copied reference VDI to GBM transfers; never edit the reference."""
def gbm_vdi(source):
    def replace_between(start, end, replacement):
        nonlocal source
        a = source.index(start); b = source.index(end, a)
        source = source[:a] + replacement + source[b:]
    source = source.replace('#include <xf86drm.h>', '#include <xf86drm.h>\n#include <gbm.h>\n#include <cstdlib>')
    replace_between('int sync_dma(', '/* Diagnostic breadcrumbs;', '')
    source = source.replace('struct Mapping { void *address; size_t size; unsigned int users; };',
        'struct Mapping { void *address; size_t size; unsigned int users; gbm_bo *bo; };')
    source = source.replace('mutable AuroraDrmDisplay display_ = {};', '''mutable AuroraDrmDisplay display_ = {};
    mutable gbm_device *gbm_ = nullptr;
    bool device() const {
        if (gbm_) return true;
        if (display_.fd < 0 && AuroraOpenDisplayDrm(&display_, 0)) return false;
        gbm_ = gbm_create_device(display_.fd); return gbm_ != nullptr;
    }
    static uint32_t fourcc(int format) {
        switch (format) {
        case PIXEL_FMT_RGBA_8888: return GBM_FORMAT_ABGR8888;
        case PIXEL_FMT_RGBX_8888: return GBM_FORMAT_XBGR8888;
        case PIXEL_FMT_BGRA_8888: return GBM_FORMAT_ARGB8888;
        case PIXEL_FMT_BGRX_8888: return GBM_FORMAT_XRGB8888;
        default: return 0;
        }
    }
    static bool transfer(const BufferHandle &h, Mapping &m, bool upload) {
        uint32_t pitch = 0; void *cookie = nullptr;
        void *p = gbm_bo_map(m.bo, 0, 0, h.width, h.height,
            upload ? GBM_BO_TRANSFER_WRITE : GBM_BO_TRANSFER_READ, &pitch, &cookie);
        if (!p) return false;
        bool valid_pitch = pitch >= static_cast<uint32_t>(h.width) * 4;
        if (valid_pitch) for (int y = 0; y < h.height; ++y) {
            auto cpu = static_cast<unsigned char *>(m.address) + static_cast<size_t>(y) * h.stride;
            auto gpu = static_cast<unsigned char *>(p) + static_cast<size_t>(y) * pitch;
            if (upload) memcpy(gpu, cpu, static_cast<size_t>(h.width) * 4);
            else memcpy(cpu, gpu, static_cast<size_t>(h.width) * 4);
        }
        gbm_bo_unmap(m.bo, cookie); return valid_pitch;
    }''')
    source = source.replace('for (const auto &item : mappings_) munmap(item.second.address, item.second.size);',
        'for (const auto &item : mappings_) { free(item.second.address); gbm_bo_destroy(item.second.bo); }\n        if (gbm_) gbm_device_destroy(gbm_);')
    replace_between('        if (display_.fd < 0 && AuroraOpenDisplayDrm(&display_, 0)) {', '        BufferHandle *handle = AllocateBufferHandle', '''        if (!device()) return -1;
        uint32_t width = info.width;
        if (info.usage & ALIGN_512) width = (width + 127) & ~127U;
        gbm_bo *bo = gbm_bo_create(gbm_, width, info.height, fourcc(info.format),
            GBM_BO_USE_RENDERING | GBM_BO_USE_LINEAR);
        if (!bo) return -1;
        uint32_t pitch = gbm_bo_get_stride(bo);
        uint64_t bytes = static_cast<uint64_t>(pitch) * info.height;
        int fd = gbm_bo_get_fd(bo); gbm_bo_destroy(bo);
        if (fd < 0) return -1;
        if (bytes > INT_MAX || bytes < info.expectedSize) { close(fd); return NOT_SUPPORT; }
''')
    source = source.replace('handle->stride = request.pitch;', 'handle->stride = pitch;')
    source = source.replace('handle->size = request.size;', 'handle->size = bytes;')
    source = source.replace('munmap(found->second.address, found->second.size);', 'free(found->second.address);\n                    gbm_bo_destroy(found->second.bo);')
    replace_between('    void *Mmap(', '    int32_t IsSupportedAlloc(', '''    void *Mmap(const BufferHandle &handle) const override
    {
        Identity id;
        if (!valid(handle) || !identity(handle, id)) return nullptr;
        std::lock_guard<std::mutex> guard(lock_);
        auto found = mappings_.find(id);
        if (found != mappings_.end()) {
            ++found->second.users;
            const_cast<BufferHandle &>(handle).virAddr = found->second.address;
            return found->second.address;
        }
        if (!device()) return nullptr;
        gbm_import_fd_data desc = {handle.fd, static_cast<uint32_t>(handle.width),
            static_cast<uint32_t>(handle.height), static_cast<uint32_t>(handle.stride), fourcc(handle.format)};
        gbm_bo *bo = gbm_bo_import(gbm_, GBM_BO_IMPORT_FD, &desc, GBM_BO_USE_RENDERING);
        if (!bo) return nullptr;
        void *address = calloc(1, handle.size);
        if (!address) { gbm_bo_destroy(bo); return nullptr; }
        Mapping mapping = {address, static_cast<size_t>(handle.size), 1, bo};
        if (!transfer(handle, mapping, false)) { free(address); gbm_bo_destroy(bo); return nullptr; }
        mappings_[id] = mapping;
        const_cast<BufferHandle &>(handle).virAddr = address;
        return address;
    }

    int32_t Unmap(const BufferHandle &handle) const override
    {
        Identity id; if (!identity(handle, id)) return -1;
        std::lock_guard<std::mutex> guard(lock_);
        auto found = mappings_.find(id); if (found == mappings_.end()) return -1;
        if (--found->second.users) return 0;
        bool ok = transfer(handle, found->second, true);
        free(found->second.address); gbm_bo_destroy(found->second.bo); mappings_.erase(found);
        const_cast<BufferHandle &>(handle).virAddr = nullptr;
        return ok ? 0 : -1;
    }

    int32_t FlushCache(const BufferHandle &handle) const override
    {
        Identity id; if (!valid(handle) || !identity(handle, id)) return -1;
        std::lock_guard<std::mutex> guard(lock_);
        auto found = mappings_.find(id);
        return found == mappings_.end() || transfer(handle, found->second, true) ? 0 : -1;
    }

    int32_t InvalidateCache(const BufferHandle &handle) const override
    {
        Identity id; if (!valid(handle) || !identity(handle, id)) return -1;
        std::lock_guard<std::mutex> guard(lock_);
        auto found = mappings_.find(id);
        return found == mappings_.end() || transfer(handle, found->second, false) ? 0 : -1;
    }

''')
    return source
