# Native presentation 043 — independently verified, not deployed

## Outcome

A fresh native candidate and **345,590-byte** last-initrd overlay were built once and independently re-read and verified. No device installation, reboot or input injection has occurred for 043.

Overlay SHA-256: `b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7`.

## Actual scope of changes

- Complete candidate versus frozen 041: **666 unchanged records**; only `init`, the composer VDI and the newly formatted scratch filesystem differ. All archive metadata matches.
- Inner bootstrap source is byte-identical to 041. Outer source changes only the separate run labels. Kernel, DTB, original services, identities, security checks and automatic-return budgets remain unchanged: 240-second target observation, separate 420-second software deadline. This is not a hard-kernel-wedge recovery guarantee.
- The actual overlay contains **only** `init` and `native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so`. It reuses the verified original empty base-032 scratch member, not persistent user data.
- The VDI adds bounded actual KMS page-flip callback records, correlating client and cursor submissions separately. It does not change rendering, cursor input, fences, initial modesetting or the existing timer callback. Submission identifiers do **not** prove unique visual content.

## Evidence and checks

- Candidate: `native-original-graphics-boot-043/result.json` and `presentation-overlay-audit.json`.
- Independent re-read: `native-presentation-package-043-independent/result.json`; actual compressed overlay was decompressed and compared, not merely trusted from builder metadata.
- All three original SDK images independently rehashed; all **71** existing native-041 raw files and **378** earlier native-012 files remain intact. Existing 041 artifacts and the 043 telemetry module's guarded inputs remain unchanged.
- Explicit offline suites: telemetry/source/build 3 passed; analyzer 3 passed; telemetry artifact audit gate 1 passed; streaming package gates 3 passed. No broad discovery or replay of operational experiments.

The existing 041 FD690 GPU evidence is historical and was not rerun. Its 4.148 ms composition mean is not desktop FPS. **043 runtime, stable 120 FPS, interactive presentation, physical input and status-bar completeness remain unverified.** Existing diagnostic traces are not cryptographic identity attestations, and bounded buffering can omit a final tail.

No Ubuntu boot/default, screen-off, host security, original images or other-session code was changed. Further staging/install/boot must use fresh guards, retain the 64 MiB EFI reserve, preserve all existing EFI files and Ubuntu default, and reconnect immediately after any separately numbered authorized reboot.
