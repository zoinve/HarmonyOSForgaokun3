# Original service software EGL integration 062

## Actual outcome

Original RenderService PIDs 506 and 765, UID1003/domain render_service, really
opened DRM, created non-null GBM devices and Mesa displays, returned EGL_TRUE from
eglInitialize and created non-null GLES contexts. These observations came from
the original service graph, not a stand-alone API success substitute.

The VM used software Mesa/softpipe, TCG and a virtual GPU. This is not native
Adreno or physical display evidence. EGLMakeCurrent is not traced; neither Skia
GPU readiness nor working drawing can be inferred just from context creation.
eglCreatePbufferSurface still returned null. Static Mesa GBM configs advertise
WINDOW_BIT only, but a surfaceless path may be valid; this is not yet a proven
cause of remaining startup failure.

No Foundation critical-fault marker or guest reboot occurred within the bounded
160-second observation. RenderService506 did exit: original init reported code0
at108.601s, and765 was subsequently observed. Therefore this is **not** stable
service, compositor, SceneBoard or desktop verification. A reported child code
alone is not an independent crash/signal diagnosis.

## Preservation and evidence

- `reports/original-graphics-boot-062-independent.json` verifies the original
  UID/domains, 19 permissive-mode samples, all12 injected files, initrd/kernel,
  all3 original SDK images and all378 prior native raw-log hashes.
- Serial SHA256: c2f50075140d3e5887cf0a493d00609e97fd8d13d7838f43eb72694be16273ed.
- Initrd SHA256: 0ac3e9dd900b4dfaa5f29fcbbeaa2ec095d42bc3e8fd95909ca9d0a7d3e8e9fa.
- Trial061 stopped before QEMU because bundle008's manifest was local-only.
  Its failure remains preserved;062 used a fresh number and corrected only the
  manifest path. Completed trials were not repeated.
- No Ubuntu/MateBook connection, reboot or security/boot configuration change
  was made by this work. Guest policy support/loading remained enabled and the
  original service identities were not changed.

Read-only forensic listing of retained062 scratch failed normal debugfs metadata
checksum validation after the intentionally bounded VM termination. `debugfs -n`
(still read-only) listed an empty faultlogger directory, but this is checksum-
unchecked forensic data, not proof that no crash occurred. No filesystem repair
or replay was performed on the retained image.

## Next bounded observation

Trial063 retains the same provider/EGL/Mesa files and adds only bounded original
HiLog queries filtered to the actually discovered RenderService PID. This avoids
spending the whole log-query window printing old boot messages. It does not alter
original service code, credentials, policy or authentication and makes no success
claim before actual logs are examined.
