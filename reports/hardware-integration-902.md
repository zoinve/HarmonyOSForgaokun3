# 902: independent buffer import comparison

- Both the NativeWindow bridge and unchanged product EGL frontend passed real VirGL (FD690) context and green-pixel readback tests.
- Independently created DRM dumb buffers and GBM buffers imported successfully as real EGLImages through both EGL paths.
- The separate original ION shim could not open its heap (`errno=2`); no ION allocation/import result was obtained. This is **not evidence that the current system allocator uses ION**.
- Read-only inspection of the original top-level display-buffer VDI instead shows dependencies on `libdma_cpu.z.so` and `CpuBufHeap*` functions. Its actual allocation/import behavior requires a direct test.
- No desktop or full-system visible frame has been verified.

Fresh 903 is a diagnostic-only comparison: load the original VDI and a separately named reference DRM VDI in independent child processes, allocate only their own 13×7 and 1920×1080 buffers, write/flush pixels, import and verify real GPU readback. The system allocator is not replaced. No KMS master, scanout or CRTC changes are performed. The reference allocator build retains compiler warnings in its logging formats; these are not represented as a warning-free build.

903 archive SHA-256: `08a7c94a414b3a94d1fa29efa1c80bdebfae33e5ef45373c14e3149339db7fbe`.

902 post-run disk-integrity results and userdata cleanup are recorded separately after its runner exits.
