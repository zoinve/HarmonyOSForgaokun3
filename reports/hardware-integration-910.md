# 910: allocator backend loads and system image imports succeed

The private driver RUNPATH correction allowed the allocating service to create real GPU buffers. RenderService's actual 512×512 native-buffer EGLImage imports now return non-null images. Both standalone EGL paths still report VirGL (FD690) and pass exact green-pixel readback. The vendor-path and private allocator probes also pass exact CPU-to-GPU pixels at 13×7 and 1920×1080.

Presentation remains unsuccessful: NativeWindow requests return success, but the bridge's `copy_frame` returns false, so these frames are not flushed. The framebuffer snapshot remains at 14,012 nonblack pixels, consistent with the previously inspected boot-penguin image, not desktop evidence. QMP reports running but has no surface.

Fresh diagnostic payload 911 records the actual mmap/sync failure and errno without changing graphics behavior or consuming EGL errors. Its archive SHA-256 is `170a23f73453ddc09fb62f802634eb90d86846501090bfe1cbbca9a387652060`; the actual archive executable-mode check passed. An initial diagnostic C-string escaping build error was corrected before any completed archive existed.

910 was stopped with QMP quit. Post-run original-image integrity is reported separately when the runner completes. No genuine desktop is verified.
