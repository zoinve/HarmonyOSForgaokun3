# Original graphics 057: actual display initialization failure

The bounded original-init run completed once in isolated, headless ARM64 TCG.
It again ended with a guest Foundation critical fault and guest reboot, not a
working desktop. Ubuntu was not connected to or changed in this sequence.

## Verified evidence

- `original-graphics-boot-057-independent.json` checks the raw serial hash,
  archive, kernel, all twelve injected files, three original SDK images and
  all 378 retained native raw logs.
- Serial SHA-256:
  `4f18aa7e8284a187b139afde3aa741c109bb0d82fc3bec6648d5aa41215e879b`.
- All 21 recorded SELinux samples are permissive. Original RenderService UID
  1003/domain, composer UID 3036/domain and allocator UID 3041/domain remain.
- Original RenderService processes 507, 814, 896, 989 and 1057 produced real
  bridge constructor and Mesa-load witnesses, then `bridge_error=0x3001`
  (`EGL_NOT_INITIALIZED`, errno 2). No forwarded `eglInitialize` result appeared.
  The observed initialization fails earlier; no EGL context success is claimed.

## Narrowing the actual failure

058 changes only reversible logging at the DRM-open, GBM-device and Mesa-display
boundaries, retaining real calls, returns, error state and original service code.
It reuses the verified 056 bootstrap and is a fresh operational run.

Independent static inspection found an omitted runtime search-path requirement:
the unchanged `libgbm.so.1` embeds `/system/lib64/lab-virgl883/gbm`, while the
fixture exposes the real backend at `harmony-mesa/gbm` and previously supplied
only the separate `lab-softpipe-167` RUNPATH alias. Mesa's
`src/gbm/main/backend.c:109-165` dynamically searches for `dri_gbm.so`; this
dependency is not in `DT_NEEDED`. The backend ELF itself is already packaged.
This is a concrete packaging mismatch, not yet proof of the runtime failure
branch. Prepared 059 adds only the missing directory alias inside the volatile
system overlay, without ELF patches, environment overrides or credential changes.

No complete composer request, stable RenderService, desktop or physical scanout
is verified. The Foundation failure is retained, not suppressed.
