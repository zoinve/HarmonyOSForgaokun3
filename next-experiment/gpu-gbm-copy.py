"""Replace raw dma-buf mmap with genuine GBM transfer of a typed buffer."""
def gbm_copy(source):
    start = source.index('    void *memory = mmap(nullptr, buffer.size', source.index('bool copy_frame'))
    end = source.index('    bool rgba = ', start)
    setup = '''    uint32_t format = 0;
    switch (buffer.format) {
    case PIXEL_FMT_RGBA_8888: format = GBM_FORMAT_ABGR8888; break;
    case PIXEL_FMT_RGBX_8888: format = GBM_FORMAT_XBGR8888; break;
    case PIXEL_FMT_BGRA_8888: format = GBM_FORMAT_ARGB8888; break;
    case PIXEL_FMT_BGRX_8888: format = GBM_FORMAT_XRGB8888; break;
    default: return false;
    }
    gbm_import_fd_data descriptor = {buffer.fd, uint32_t(buffer.width),
        uint32_t(buffer.height), uint32_t(buffer.stride), format};
    gbm_bo *bo = gbm_bo_import(display.device, GBM_BO_IMPORT_FD, &descriptor, GBM_BO_USE_RENDERING);
    if (!bo) return false;
    uint32_t mapped_stride = 0; void *cookie = nullptr;
    void *memory = gbm_bo_map(bo, 0, 0, buffer.width, buffer.height,
        GBM_BO_TRANSFER_WRITE, &mapped_stride, &cookie);
    if (!memory) { gbm_bo_destroy(bo); return false; }
    if (mapped_stride < uint64_t(buffer.width) * 4) {
        gbm_bo_unmap(bo, cookie); gbm_bo_destroy(bo); return false;
    }
'''
    source = source[:start] + setup + source[end:]
    start = source.index('    sync.flags = DMA_BUF_SYNC_END', source.index('bool copy_frame'))
    end = source.index('\n}', start)
    source = source[:start] + '''    gbm_bo_unmap(bo, cookie);
    gbm_bo_destroy(bo);
    return true;''' + source[end:]
    old = 'static_cast<unsigned char *>(memory) + size_t(y) * buffer.stride'
    assert source.count(old) == 1
    return source.replace(old, 'static_cast<unsigned char *>(memory) + size_t(y) * mapped_stride')
