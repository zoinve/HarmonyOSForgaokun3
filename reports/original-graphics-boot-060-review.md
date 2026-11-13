# Original graphics060: real loader evidence and driver selection

- Actual original RenderService (UID1003, original SELinux domain) still fails
  GBM creation after successful DRM open. The backend is readable (`access=0`).
  It has not reached EGL initialization. Guest SELinux remained permissive in
  all20 captured samples; Foundation reported a critical fault.
- Independent verification: `original-graphics-boot-060-independent.json`.
  Serial SHA256 `735e23249bc3387ae3a6db1670138e79a7d5e941d8d961e8ef7299a7721f61dc`.
  All12 injected ELFs, original images, kernel and378 prior native logs checked.
- The loader diagnostic mentions `gbm/tls/dri_gbm.so`; Mesa first tries that
  optional TLS path before the normal path. That error alone is not proof that
  the normal backend cannot load, nor is errno38 a proven cause.

## Configuration defect found

The packaged Gallium's `.text` and `.rodata` hashes exactly match the existing
`mesa-build` output. Its Meson configuration enables only `gallium-drivers=virgl`.
The current virtual GPU has no VirGL3D host backend. In particular, the packaged
library has no `softpipe_create_screen` implementation. This is not an adequate
software-rendering fallback for the no-host-GPU integration fixture.

`original-softpipe-001/result.json` records an isolated real softpipe build,
without downloads or installation, preserving existing Mesa/source guards.
`original-graphics-egl-008/result.json` replaces precisely six coherent Mesa
libraries while preserving the traced bridge, libdrm and scoped NDK runtime.
Original platform libc++, service executables, identities and policy are unchanged.
This is an isolated VM software route, not a substitute for native Adreno support.

## Pending runtime validation

Trial061 stopped before QEMU because the inherited launcher expected a duplicate
manifest at a path bundle008 does not publish. Its failure is preserved; no rerun.
Trial062 corrects only the manifest source path and tests the software bundle in
the same original-init fixture. No success, desktop or physical scanout is claimed
before actual runtime evidence. No MateBook/Ubuntu host changes were made.
