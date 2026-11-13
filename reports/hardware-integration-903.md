# 903: independent allocator comparison

Native ARM/KVM, VirGL/FD690, no physical viewer. System allocator unchanged.

Actual results (`next-experiment/diagnostic-903.txt`):

- Original vendor VDI: own 13×7 RGBA buffer allocation succeeds; real EGL DMA-BUF import fails, `EGL_BAD_ALLOC` (0x3003), child exit 4.
- Separately named reference DRM-dumb VDI: allocation and real EGL import succeed; reading the CPU-written color through the GPU returns `(0,0,0,0)`, not `(64,128,191,255)`, child exit 2. Import success alone is insufficient.
- Both existing standalone EGL paths still pass their VirGL GPU-clear/readback checks.

No KMS master/CRTC changes or service allocator replacement were made. No desktop verified.

Next isolated comparison: actual Mesa GBM BO CPU map/write/unmap → export → EGL import → GPU pixel readback, at 13×7 and 1920×1080. This tests transfer semantics without adopting an unverified allocator. Fresh payload 904 SHA-256: `35ec3c09781607a0e3e7e540a7d044406a1463df7fc385c8622be2dd7ff8c5e2`.

903 was stopped gracefully; post-run original-image verification and userdata cleanup are recorded separately after completion.
