# 912: NativeWindow presentation recovered

- Original product EGL frontend and bridge both report VirGL (FD690), with genuine green-pixel readback passing.
- New GBM allocator passes 13×7 and 1920×1080 import/pixel comparisons.
- RenderService now completes NativeWindow request, GBM-backed copy, flush and swap successfully.
- Independent real-GPU NativeWindow fixture reports `EGL_WINDOW_BRIDGE_PASS`: orientation, format, resize, pack state, failure recovery and image lifetime. Child status 0.
- Actual guest fbdev snapshot has 4,652 nonblack pixels. `next-experiment/run-912/framebuffer-snapshot.png` visibly shows the genuine OOBE welcome arrow, not Linux boot penguins and not a desktop.
- QMP still reports `no surface`; this is not used as evidence that the guest framebuffer is blank.

Fresh 913 changes only diagnostic capture: a bounded own child reads fbdev every 15 seconds into an atomically replaced private snapshot. This enables verified headless navigation without changing rendering, services or physical screen state. Payload SHA-256: `91681106434a5657832217c90428838d1e5a2538d95507c50e903f8d9665b793`.

No desktop verified. Post-run original-image integrity is recorded separately by the runner.
