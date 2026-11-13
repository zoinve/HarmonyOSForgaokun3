# Native 044 — original `/mnt` runtime mount regression

## Installed, not yet selected at this report's creation

- The independently audited 044 overlay adds the genuine `init_early` `/mnt` tmpfs setup: `MS_NOSUID`, mode 0755, then **MS_SLAVE**. Original root read-only configuration, policy, service identities, authentication, GPU rendering and the 043 telemetry module remain unchanged.
- Overlay: **699,477 bytes**, SHA-256 `1c4aa6a12e636430f7892a709fd60ef1fd133df4bb55ac3ea0624d1b3c3d29d1`; exactly `init`, `native-target/bootstrap`, and the unchanged composer VDI. The original empty base-032 scratch image is reused. No original SDK or persistent user data is written.
- Fresh inventory, inert staging and installation each succeeded once. Both real ARM64 entry binaries refused ordinary execution with status **77**. All **104** pre-existing EFI files remained byte-identical during installation.
- Counted entry: `native-original-graphics-044+1.conf`; Ubuntu persistent default unchanged, no one-shot selection or reboot requested by installation. Free ESP space **70,201,344 bytes**, above the retained **64 MiB** reserve. Original 031 kernel/DTB and 032 base initrd hashes remain pinned.
- Starting Ubuntu boot ID: `23d7ecf4-a2da-4c8f-87ba-dde41c90c5a7`. This is a separately numbered experiment, not a rerun of 043.

## Runtime and evidence gates

- New executor selects only its own nonce-guarded counted entry and requests exactly one reboot. SSH observation starts immediately, accepts only a changed boot ID with the expected Ubuntu kernel, and never bypasses host-key checks or automatically requests another boot.
- Original diagnostic target is **240 seconds**, outer software fallback **420 seconds**, panic timeout **15 seconds**. This is not a hardware-watchdog or hard-kernel-wedge recovery guarantee. No automatic input is injected.
- Collector uses read-only `noload,nodev,nosuid,noexec` access to the identified lab partition and unmounts it afterward. The measured HiLog exception remains 128 MiB only for `interactive-hilog030.log`; other files remain bounded at 64 MiB, total 512 MiB.
- Independent return verification requires actual native-044 and `/mnt` runtime markers, strict kernel/service evidence, hashes of all new raw files, previous 043 and 041 raw evidence, 378 older native files, and all three original SDK images. Ubuntu default, firmware, no pending one-shot, logical automatic screen-off and unmounted lab are checked. Fresh `loader/random-seed` entropy is never restored.
- KMS journal format remains **NATIVE_PRESENT043** because the telemetry module is unchanged. Submission IDs are not visual-content IDs; initial modesets and cursor-only updates are not client-frame FPS proof. Stable 120 FPS, physical input acceptance and an unlocked desktop are **not verified** by installation.

Offline checks: runtime/deployment suites **3 + 3 passed**; previous candidate mount/package audit remains immutable. Runtime, actual SceneBoard startup and completion measurements are pending at this report's creation. No old experiment or completed verifier was rerun, and no login, sandbox, watchdog or freeze protection was disabled.
