# 905: independent GBM VDI import and pixels pass

System allocator unchanged. Actual `next-experiment/diagnostic-905.txt`:

- Original vendor VDI: own 13×7 buffer import fails, EGL 0x3003, child exit 4.
- Private `gpu905-buffer-vdi.so`: both 13×7 and 1920×1080 allocate and import successfully. CPU-written pixels read through VirGL/FD690 are exactly `(64,128,191,255)`; child exit 0.
- Both unchanged standalone EGL frontend checks still pass real hardware-clear/readback.

New plugin uses typed GBM allocation and import, stable CPU staging, GBM map/unmap transfers for upload/download. The copied reference's protected-buffer rejection, metadata methods and original BufferHandle ABI checks remain. It does not take KMS master or install a system allocator alias.

Next independent test 906 keeps CPU mappings alive to test FlushCache before Unmap, then writes through the GPU and checks InvalidateCache returns the new pixels. This is necessary before service integration; 905 alone does not prove those behaviors.

906 payload SHA-256: `124f2349de0ec573cc06a5368325bb5c1604c295ae5a1857b37548ef2ed5171c`.

No desktop verified. 905 stopped gracefully; integrity verification and authorized userdata deletion are recorded separately when complete.
