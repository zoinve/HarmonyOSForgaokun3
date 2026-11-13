# Native allocator diagnostic013

## Intent and controlled changes

Run the private render-node allocator payload already verified on Ubuntu (`baremetal-buffer-vdi-run-004/independent-verification.json`) under the native profile003 kernel. This is an offscreen buffer-allocation/coherency test, not a compositor, modeset, desktop or full HarmonyOS boot.

Relative to diagnostic011, independent archive comparison found exactly one changed existing record (`opt/native-mesa-001/probe`) and 25 additional private library records. All other records, including init, launcher, identity helper, kernel modules and existing Mesa libraries, are unchanged. The additional files include the current original SDK BufferHandle implementation and its actual dependency closure; no system libraries or SDK images are replaced.

* Archive: 33,139,698 bytes; SHA-256 `17b8eb520e7185c568520cc2e4c1e5d1eb168058a98cbbb23e28e78dcf79e3d7`.
* Native kernel: `4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`.
* DTB: `2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32`.
* Original SDK 56-byte BufferHandle ABI and reserve offset48 passed on Ubuntu and subsequently on the native kernel in trial010; see `baremetal-native-trial-010-review.md`.

## Verification and safety

`baremetal-diagnostic-init-013/independent-verification.json` verifies all 620 parent records byte-for-byte with ownership/modes, all 34 private ELF file hashes, the known libc symlink, unchanged binaries, and the exact old011/new013 archive difference. Packaging012 failed on an inherited manifest-field assumption; its failure is preserved. Fresh013 uses the actual dependency-presence assertion and the separate successful runtime evidence, without inventing an all-strong-symbol-closure claim. The initial verifier failed locally on an escaped-newline anchor before remote execution; the corrected verifier completed independently.

Staging verified all six assets on the MateBook and actually executed the three ARM64 refusal paths (init, identity helper, launcher), each returning77 with the expected guard message. All 264 prior raw evidence files were checked locally and remotely before and after restoring only the isolated lab mount to RW.

The launcher remains UID/GID65534, empty supplementary groups/capabilities, NNP, private PID/mount/network namespaces, read-only private libraries and renderD128-only graphics access. No primary DRM node or display-mode changes. The existing 25-second phase timeout, 180-second best-effort overall deadline and 30-second reserve remain; kernel hangs/uninterruptible I/O recovery is not guaranteed.

The diagnostic requires `harmony.diag=1 enforcing=1`, checks active SELinux/initial enforcing, but loads no policy. It must not be described as loaded-policy GPU authorization. CPU↔GPU test synchronization uses `glFinish`; asynchronous allocator/compositor fence contracts are not proved by this run.

Trial009 installation stopped before EFI writes because the unchanged 64MiB free-space reserve would be violated. Only the unreferenced historical004 EFI assets were archived with verified bytes, then fresh trial010 installed and booted candidate013 without weakening that reserve. Trial010 independently verified all 302 collected logs and the changed Ubuntu boot ID. Both 13×7 and 1600×2560 buffers passed CPU→GPU and GPU→CPU exact-pixel checks with glFinish. Ubuntu's persistent default and logical screen-off state were verified without display setters. Cleanup007 archived and removed only the consumed013 entry, preserving all 82 other EFI files. The native allocator boundary is verified; full composer/desktop and asynchronous ownership contracts remain unverified.

Reference provenance: HarmonyMac's fixed56-byte ABI and copied GBM adaptation were reviewed; original reference files are unchanged. The second user-provided project's identity remains unresolved and is not claimed reviewed.
