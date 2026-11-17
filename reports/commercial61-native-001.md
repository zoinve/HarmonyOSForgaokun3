# Commercial ISO native boot probe 001

## Requested source and acceptance boundary

Use `L410-HarmonyOS-Installer-20261029.iso`, not the ARM SDK. The user's “6.1” identifies this file; its original embedded metadata actually reports **6.0.0.110 / API 20**. No version, device identity or permission result is fabricated to reconcile that naming difference.

ISO SHA256: `25133f67c989084649b97a0ca577a640a28af27dbaf9a411ea7e87a4a795c0e2`.

The installer itself is never executed: it repartitions disks for L410. Its four filesystem images were hashed directly out of the concatenated payload and match the already extracted local originals. Previous remote `disks-744` copies do not match those whole-image hashes, so they are preserved unused and fresh verified copies are staged under `commercial61-original-001`.

## Minimal MateBook boot glue

- Reuse the MateBook 031 kernel and DTB, Linux modules, firmware and static Linux bootstrap. Do not reuse SDK init, system/vendor libraries, graphics adapters, Bluetooth substitutions or SDK service configurations.
- Mount original commercial system, vendor, sys_prod and chip_prod images read-only, with ext4 journal replay disabled. Validate loop device sizes and read-only state. Never attach the previous commercial user-data image.
- Use a fresh 3 GiB volatile data filesystem, an isolated PID/mount/network namespace and a restricted device tree without physical storage block nodes.
- Keep commercial `/system/etc/init.cfg`, service configurations and libraries unchanged. Bind a RAM-backed board mount declaration over the L410-specific second-stage fstab because these four filesystems are already mounted; no L410 physical by-name paths are exposed.
- Retain SELinux support and policy loading. Apply the already authorized permissive configuration in RAM; do not disable SELinux or change Ubuntu security configuration.
- Execute original commercial `/system/bin/init --second-stage`. Export bounded original hilog/fault evidence and passive process/version observations.
- Limit the target session to approximately 240 seconds. An independent outer process requests reboot after 420 seconds if normal shutdown stalls; software watchdogs cannot recover every kernel/firmware hang. Ubuntu remains the default and the existing manual GPU entry remains intact.
- Preserve the user's persistent disabling of `harmony-lab-screen-off-001.timer`.

This probe does not pretend that L410's Mali graphics implementation is compatible with the MateBook FD690. Kernel startup, successful original init execution, original service startup and a working desktop are separate acceptance levels.

## Build verification and current state

Source/isolation checks passed after a failing missing-builder test. Both static ARM64 bootstrap programs compiled with `-Wall -Wextra -Werror`. The initial outer link lacked the diagnostic-core object; the failed log is preserved and the corrected successful attempt has a separate log suffix. No device was modified by that build failure.

Initrd SHA256: `f90233a25f0609c4a23f5a5168cffe2efa1cc1f20d00f2966cef0e1be00fa148`.

The four fresh image transfers completed and all original hashes were verified again before installation. Both actual native non-PID1 execution guards refused with exit 77. A unique commercial entry and 25,489,285-byte initrd were installed while all 92 prior EFI file hashes, the Ubuntu default, firmware entries, disabled custom screen-off timer and previous manual GPU entry were preserved. No files or partitions were deleted or overwritten. EFI free space after installation is 44,724,224 bytes.

## Actual boot result

One bounded boot ran on 2026-11-13, 06:39:23–06:44:44 UTC and automatically returned to Ubuntu. No retry or repeat operational experiment was performed. Current Ubuntu boot ID is `743a6992-523b-4933-9ea3-9b1347c51b1b`.

**The commercial kernel-to-userspace handoff works, but a usable commercial desktop did not start in this test.** The kernel is the retained MateBook adaptation kernel, not the ISO's incompatible L410 kernel. Captured PID-namespace observations repeatedly show original commercial `/system/bin/init --second-stage` as PID 1 after exec. Original samgr, foundation, access-token, storage, multimodal-input and multiple HDF host processes were observed. There are 104 unique observed command lines, not 104 proven healthy services; the initial conservative `runtime-analysis.json` lists only absolute-path commands and therefore its 20-command subset is not a full service count.

The display path remains blocked: original HDF service manager SA 5100 is unavailable, composer hosts repeatedly wait for it, and foundation cannot connect to RenderService. No hdf_devmgr, render_service or SceneBoard process was observed in the periodic process snapshots. The precise reason hdf_devmgr is not starting has **not** yet been established; these logs do not justify claiming that GPU hardware, a particular driver or one permission check is the sole cause. No SDK service/library substitution was introduced to conceal this failure.

All 48 sampled SELinux mode observations are `0` (permissive, not disabled). The test ended at its configured target timeout and the target namespace was stopped with status 9; this stop is the deliberate test boundary, not evidence of a spontaneous OS crash.

## Returned evidence and preservation

- Retrieved 67 files with matching remote/local hashes from `commercial61-native-001-d0ce8418-671a-4d70-b3c6-4c41a68c4297` using a read-only, no-journal-replay mount. The original LAB partition was then unmounted.
- Rehashed all four commercial images after the actual boot: all still match the original ISO contents. Original user-data was never attached and no commercial or Ubuntu partition was overwritten.
- Ubuntu is current and default, no one-shot selection remains, firmware entries and the previous manual GPU entry are preserved, and the custom forced-screen-off timer remains persistently disabled.
- All 91 non-boot-managed pre-existing EFI files remain unchanged. The only prior file changed by boot was systemd-boot's `loader/random-seed`; it was correctly allowed to rotate and was not restored.

Key evidence: `runtime-analysis.json`, `graphics-startup-analysis.json`, `post-return-verification.json`, `boot-observation.json`, and `runtime-evidence/retrieval-manifest.json` under `reports/commercial61-native-001/`. Original hilog SHA256: `b866eb19bde0946b73432b1599f23024de20d94e78b04c8b6a800d286b50bcd3`.

These remain local evidence, not published images. A subsequent commercial-board adaptation should first establish why the original HDF service manager is absent, then connect the original commercial graphics services to the real MateBook hardware. It must not call this initial process-level boot a working desktop.
