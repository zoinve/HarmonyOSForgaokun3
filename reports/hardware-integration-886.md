# Full-system 886: GBM initialization repaired

The 886 payload includes the previously omitted `gbm/dri_gbm.so` and supplies its real directory through `GBM_BACKENDS_PATH`. Original system images remain read-only; all library substitutions are RAM mounts.

Actual diagnostics:

- The private Mesa bridge initializes EGL 1.5 successfully, `EGL_SUCCESS`, child status 0.
- The unchanged OpenHarmony EGL frontend also initializes EGL 1.5 successfully, vendor `OpenHarmony`, child status 0.
- RenderService maps the intended Mesa, bridge and SDK C++ runtime alongside the unchanged product EGL/GLES frontends and platform C++ runtime.
- QEMU remains running, but `screendump` reports `no surface`. There is no actual desktop or full-system rendering success yet.

Evidence: `next-experiment/diagnostic-886.txt`, `next-experiment/gpu-886-log-extract.txt`. Missing optional `virtio_gpu_gbm.so` and `tls/` lookup candidates appear in loader logs; the eventual real DRI backend succeeds in the standalone initialization probes, so those preliminary lookup failures alone are not a new root cause.

Fresh diagnostic payload 887 changes no rendering libraries. It adds standalone product-EGL context/configuration/readback tests and reads the relevant RenderService environment. Its result must distinguish display initialization from a working context and from actual NativeWindow presentation. QMP quit was requested gracefully; post-run integrity results are reported separately.
