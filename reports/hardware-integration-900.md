# 900: black pixels already precede Composer

Native ARM/KVM, VirGL/FD690, unchanged product EGL/GLES frontends, and the existing RAM-only graphics overlay.

- Both standalone frontend tests rendered and read back the expected green pixels.
- The first three observed full-size RenderService readbacks contained zero nonblack RGB pixels; center RGBA was `0,0,0,0`. These are early samples, not proof that all subsequent rendering is black.
- NativeWindow requests, copies, flushes and Mesa swaps returned success.
- A read-only Composer client-buffer duplicate succeeded through `pidfd_getfd`. Its 1920×1080 RGB contents were all black. This observation did not request a DMA cache synchronization and has that limitation.
- The actual framebuffer was also entirely black. No genuine desktop has been verified.

Fresh diagnostic payload 901 adds bounded image-import/result tracing and sparse later readback samples. It does not change rendering returns, consume EGL errors, modify original images, or bypass drawing. SHA-256: `7409083cb601af0be2414a78939c05d7a6c1b1d6fa0145b0b4e654caa08b8c80`.

899's protected original-image checks passed. Its launcher failure was a screenshot/QMP socket race after an external graceful quit, not evidence of a GPU crash. 900 post-run integrity is recorded separately after shutdown.
