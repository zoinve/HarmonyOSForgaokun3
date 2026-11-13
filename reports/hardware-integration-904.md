# 904: GBM CPU-to-GPU transfer verified

Independent buffers only; system allocator unchanged, native ARM/KVM and VirGL FD690.

Actual `next-experiment/diagnostic-904.txt`:

- Original vendor VDI buffer: real EGL import fails, error 0x3003.
- Reference dumb-buffer VDI: import succeeds but GPU sees zero instead of the CPU-written color.
- GBM BO map/write/unmap → exported DMA-BUF → EGL image → GPU readback: **both 13×7 and 1920×1080 return exactly (64,128,191,255)**. Child exits 0.
- Existing original OHOS frontend GPU-clear/readback test also passes.

Mesa 25 `gbm_dri_bo_unmap` explicitly unmaps the DRI image and flushes its mapping context; the dumb-buffer mapping path lacks that transfer. This supports using proper GBM transfers rather than treating import success or DMA-BUF cache ioctls as sufficient.

Next independent plugin 905 adapts the copied reference allocator to typed GBM allocations, stable CPU staging memory, GBM upload on FlushCache/Unmap and download on InvalidateCache. Protection/format validation, original BufferHandle allocation ABI, metadata and service identities are retained. No system allocator alias/bind is installed. Runtime validation remains pending.

Payload 905 SHA-256: `bfa139c5b6358435787ff0c625c35c74f62d767a1534f4aa5c2276a583e6ffb9`.

No desktop verified. 904 stopped gracefully; post-run integrity and userdata deletion are recorded separately.
