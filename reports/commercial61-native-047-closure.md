# Commercial 047 partial-evidence closure

The only boot began 2026-11-14T13:45:36.440212Z and Ubuntu was observed
again at 13:47:12.957184Z, boot ID 477eff1c-4ca3-47d7-b2d0-8052734f774e.
This early return is not proof of a normal target timeout. Do not rerun 047.

Kernel and modules were rebuilt together. The initrd module dependency
closure and regenerated indexes were verified, all included kernel modules
and unchanged-source ashmem have 1216-byte module structures, and the ordered
incremental chain equals the full initrd. The original inner bootstrap is
byte-identical to 046; no original service or authentication check changed.

The run directory exists. Standard ro,noload retrieval failed because 15
later directory entries cannot be stat'ed (EBADMSG). A separate read-only
partial retrieval preserved phase-001 through phase-027, 27 files total,
with every remote byte count and hash verified. The manifest records all
15 errors: phase-028 through phase-040 plus both interactive logs. No
journal replay, filesystem repair, forced module loading or second boot
was performed. The original partition is unmounted.

The final readable cumulative log proves PCIe PHY and NVMe probes succeeded,
lab storage opened successfully, all listed board/display/input module
probes returned status zero, and a DRM node was observed. This is not pixel
evidence. It does not prove original-service probe registration, SceneBoard
execution, desktop output or interaction. No readable target-exit or panic
evidence currently establishes why the boot returned early.

A read-only debugfs stat of the phase-040 directory target reports an inode
with zero mode, size, links and timestamps on the un-replayed filesystem.
This does not prove permanent corruption: committed journal metadata may
not yet have been checkpointed. Ubuntu dmesg inspection did not supply the
target panic. Any recovery must preserve the original partition and clearly
distinguish supplemental recovered evidence from the verified readable set.

The post-return verifier passed: 109 prior EFI files unchanged, normal
random-seed update, archived/authorized removal of entry 045 accounted for,
firmware and all four commercial images unchanged, Ubuntu current/default
preserved, original manual entry retained, and screen-off timer enabled and
active. Experimental entries retained are 046 and 047; shared payloads remain.

Native desktop pixels and interaction remain unverified. Next obtain the
missing startup/trace/exit evidence without replaying the original evidence
partition or inventing a target failure diagnosis from absent logs.

## Supplemental recovery

An independent sparse metadata image was created with e2image in a new
commercial-recovery-047 directory on the Ubuntu filesystem. Journal-only
replay was applied exclusively to that regular image file. Replayed inode
and block mappings were then used to read file content from the original
block device opened O_RDONLY. The original remained unmounted and its
superblock bytes were unchanged. No original filesystem repair occurred.

All 42 files were recovered without mapping errors. All 27 previously
readable files are byte-identical, including their verified sizes and hashes.
Supplemental bytes, block provenance, copy-replay logs and comparisons are
under recovered-evidence, separate from the original partial retrieval.

Recovered phase-040 confirms original commercial init handoff and original
service startup, reaching outer sample index 2. Recovered hilog reaches the
original RenderService's first eglSwapBuffers entry at guest 16.974 seconds.
No TRACE_READY or TRACE_SETUP_FAILED marker appears in the recovered phase.
These incomplete logs do not establish whether registration started, whether
any probe was enabled, why the machine returned, or whether it panicked.
The old inference that no runtime handoff evidence exists is superseded;
native desktop and interaction are still unverified.
