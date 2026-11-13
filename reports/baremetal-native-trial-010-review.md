# Trial 010: native allocator boundary

## Verified outcome

Candidate 013 ran the private render-only allocator probe on native kernel `7.1.0-rc3-gaokun3-el2`, then returned to Ubuntu `7.1.0-rc3-gaokun3+`, boot ID `8f037a5e-ea09-45cf-8135-d2e3bb2a2cdd`.

- Actual original-SDK BufferHandle allocation passed: 56-byte header, reserve-count offset 48, two reserved FDs and three reserved integers.
- Renderer was FD690. The copied reference VDI used the render node, not the primary/KMS node.
- 13×7 buffer: stride 256. 1600×2560 buffer: stride 6400.
- Both geometries passed CPU shadow write → FlushCache → EGL DMA-BUF import → GPU readback: RGBA `64,128,191,255`.
- Both passed GPU clear → **glFinish** → InvalidateCache → CPU readback: RGBA `191,64,128,255`.
- Probe, launcher and enclosing `native-mesa-offscreen` phase all exited 0. Every recorded phase ended with status 0.
- Actual sandbox admission: UID/GID 65534, no supplementary groups or capabilities, no-new-privileges, private PID/mount/network namespaces and no primary DRM node.
- The diagnostic identity helper passed protocol 8 / features 5, traditional Binder, active SELinux and initial enforcing=1, with zero task identities and no identity/permission writes. **No policy was loaded by this diagnostic.**

## Independent evidence and return

All **302** collected raw-file sizes and SHA-256 values matched the collector manifest, checked separately from collection and by the return verifier. There are 264 historical files and 38 new **cumulative snapshots**, not 38 independent tests.

New directory: `native-diag-001-d7225c62-c608-424b-9cdc-7f9fd34ef5bc`.
Final snapshot `phase-038.log`: 112781 bytes, SHA-256 `8fcb94d2cae356339d4c72b927fade324fc4da101583e7b335bcfecb4cbb05de`. Its device-tree model NUL is preserved.

The immediate reconnect started at approximately 0.0000013 seconds and admitted the changed Ubuntu boot ID after 58.145 seconds / 16 probes. This is observation latency, not an exact boot-duration measurement.

`baremetal-native-trial-010-independent-verification.json` confirms the persistent Ubuntu default, absent one-shot selection, successful enabled/active screen-off timer, and GDM already logically off. The verifier refused display setters; physical screen state was not observed.

The only tracked pre-existing EFI change across reboot was `loader/random-seed`: `c9d9bddccc7d0e371aeede3ab6fa14465852d9ba2fd7e9406f5cf2de99f8327d` → `198cacf054b22b1ff1badc4204a1416033e86c3b7f3eff71ad6b90e80e2a2674`. Do not restore stale seed bytes or claim every EFI byte stayed unchanged after boot.

## Limits and next boundary

This is the first verified allocator ABI / two-way CPU–GPU coherence result on our own native kernel, extending the earlier Ubuntu-only VDI004 test. It does not verify cross-process handle ownership, every format/usage, synchronization without glFinish, loaded-policy GPU authorization, composer integration, physical scanout/touch events, or a native HarmonyOS desktop. Existing early SDK IPC and original-init QEMU tests retain their separate security scopes.

No screen mode, Ubuntu libraries, original SDK images, authentication data or persistent boot default was changed. Cleanup 006 was launched separately to archive and remove only the consumed 013 entry after the 302-file verification; its result is not inferred here.

### Consumed-entry cleanup result

Cleanup 006 stopped at its local exclusive-output guard: the preflight had inadvertently executed the generated launcher's local top-level backup creation. No remote cleanup was performed by that failed invocation. Its local backup and failure are retained. The corrected fresh 007 preflight inspected the AST and compiled its remote literal without executing the launcher.

`boot-entry-cleanup-007.json` confirms that cleanup 007 archived the exact consumed 013 config locally and in `/var/lib/harmony-lab-boot-entry-cleanup-007`, then removed only `loader/entries/harmony-native-diag-013+0-1.conf` (SHA-256 `095ec13278dcf73b05382b33c5889c005903deba791be01874cbb1e89accb7e2`). All 82 other EFI files stayed byte-identical; persistent Ubuntu and firmware defaults stayed unchanged. No additional reboot occurred. Assets and raw logs remain preserved. Future trials require a fresh post-cleanup baseline; do not rerun trial010's installer or runner.
