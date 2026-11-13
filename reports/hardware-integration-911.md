# 911: WSI fails at ordinary dma-buf mmap

- Actual RenderService traces repeatedly report `GPU911_COPY_FAIL stage=mmap ... errno=13` on 1920×1080 typed buffers. Real native-buffer EGL imports succeed.
- Both independent EGL paths still report VirGL (FD690), exact green-pixel readback, and successful child exits. This is not a loss of GPU context support.
- A fresh 912 payload replaces WSI raw mmap/DMA-sync writes with typed GBM import, map-write using the returned pitch, unmap/upload, and cleanup. Format conversion, vertical orientation, real GL readback, protected-buffer rejection and GL-state preservation remain.
- An independent mock NativeWindow fixture uses real GBM allocator buffers and the actual bridge to check pixel orientation, format, resizing, pack/PBO/FBO state, queue failures and image lifetime. It does not change KMS master/CRTC state. Its runtime result is not assumed.
- 912 archive SHA-256: `16db2184f3b6cd3bbe05d3a6059561b83fbe43e09846796f314eb1430e05cf05`.

No genuine desktop is verified. Original-image post-run checks are reported by the runner separately.
