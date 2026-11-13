# Original RenderService GBM backend: trial059

Adding the genuine packaged GBM backend's compile-time path alias did **not**
resolve initialization. With the same EGL006 binaries, real original
RenderService processes493,776,882,995,1066 still recorded successful DRM open,
NULL GBM device and EGL_NOT_INITIALIZED. The observed errno at the GBM boundary
changed from2 to38; errno alone is not an identified root cause.

Trial059 ran once for the160-second observation bound. It was terminated by the
runner at that bound, not a clean service shutdown. A Foundation critical fault
was observed; no guest reboot was captured before the bound. All20 observed
SELinux samples were permissive. Original composer/allocator/RenderService UIDs
and domains, both VDI mappings and original RenderService's EGL/Mesa mappings
were observed. This establishes neither stable services nor a desktop.

Evidence: `reports/original-graphics-boot-059-independent.json` independently
verifies all12 injected files, initrd, kernel, the three original SDK images and
378 earlier native raw files. Serial SHA-256:
`a1a10efb785f6fdb397612b4e51268521f10373dcb162fdf0bc02df83cf8a92a`.
The preserved RAM scratch SHA-256 is
`45070dc36d34214aff9a5f1ab3db95cfbf927cfbad2e585705f7f3b9f65de328`.

Trial060 retains this exact bootstrap/configuration and Mesa closure, adding
bounded failure-only diagnostics to the copied reference EGL bridge. It reads
the actual loader error after GBM failure, records the loaded GBM implementation
and checks backend readability. It does not retry loading, fabricate a device,
consume EGL error state, change service credentials or patch original binaries.
Its result remains pending here. No Ubuntu or physical-display changes were made.
