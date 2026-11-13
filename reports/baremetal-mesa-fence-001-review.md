# OHOS Mesa native-fence test 001

The OHOS-built Freedreno stack passed a native-fence and DMA-BUF coherence test on the MateBook GPU under the existing Ubuntu kernel. This is not a HarmonyOS desktop or candidate-kernel test.

- Renderer: `FD690`; EGL 1.5, OpenGL ES 3.2 Mesa 25.0.1.
- A linear ARGB8888 GBM buffer was exported and imported into EGL.
- GPU completion fence was exported, polled with a bounded timeout, imported into EGL with FD ownership transferred, waited and checked signalled.
- GLES readback and a second independently opened GBM device's imported-buffer CPU mapping both returned opaque red foreground and opaque blue background.
- Probe exited zero, with no new captured kernel log lines.

The transient service's effective policy was captured before execution: non-root user, supplementary render group, no capabilities, no-new-privileges, closed device policy permitting only renderD128, strict system/home isolation, private network/tmp and time/memory/task limits. Admission opened renderD128 and was denied card0. No modeset, DRM-master access or physical-screen test was performed.

Independent verification checked all nine deployed ELF files' sizes and hashes, unchanged boot/default/one-shot state, no stale on-disk diagnostic entries, and the already-off GNOME logical display state using a verifier that refuses display setters. The screen-off timer remained active.

Evidence: `baremetal-freedreno-fence-run-001/result.json` and `independent-verification.json`. Mesa's existing FD-description comparison warning remains unresolved; this passing bounded path does not prove general multi-FD identity compatibility. Cross-process unsignalled-fence behavior, compositor integration and native HarmonyOS runtime remain unverified.
