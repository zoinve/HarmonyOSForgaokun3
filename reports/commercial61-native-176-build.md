# Native176: compiled USB guard diagnostics, not deployed

Date: 2026-11-16.

## Purpose

Native175 refused before persistent-data preparation and original init handoff.
Its broad failure marker did not identify the failing syscall. Native176 keeps
the exact175 selection/protection implementation and adds fixed numeric operation
diagnostics for open, fstat, BLKGETSIZE64, BLKROGET and BLKROSET. No device contents
or serial strings are logged. Write-enabling requests remain forbidden.

## Build evidence

- Build: `/home/zoinve/harmony-virgl-883/commercial61-native-176`.
- Metadata: `commercial61-native-176/result.json` and `overlay-result.json`.
- Verification: `commercial61-native-176/build-test.json`.
- Complete 29-archive reconstruction equals the full generated initrd.
- Both ARM64 executables reproduce byte-for-byte under strict compiler warnings.
- Both retain the bounded non-PID1 execution guard under qemu-aarch64.
- 21 focused test scripts passed; the trace-wrapper suite explicitly ran four tests.
- Runtime binary and source are byte-identical to the working173 desktop baseline.
- Runtime SHA256: `fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122`.
- Minimal overlay: 381554 bytes, SHA256
  `2cceb0631daae1b1fdc3f745b9b5c4e6273a9e48e23233088e64602f034dc183`.
- Compared with full164, archive changes remain only init and its early hash wrapper.

## Limits And Next Gate

No installation workflow was added or admitted, no target files or firmware were
changed, and no native176 boot occurred. The target's latest read-only Ubuntu
enumeration showed hubs and the Huawei keyboard but no USB disk. Absence does
not establish physical unplugging or the reason for disappearance.

Before deployment: verify current USB identity and normal unmount state, preserve
current system/EFI evidence, use a hash-verified short final ESP alias within the
existing 1800 command-line bound, and admit the deployment workflow. Do not rerun
native175. Retain173 as the working desktop baseline. Compilation and fixtures
do not prove native USB-service acceptance, NTFS access or Settings repair.
