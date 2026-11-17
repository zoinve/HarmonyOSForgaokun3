# Commercial 004: one additive MateBook board import

## Minimal change

003 records init requesting the absent `/vendor/etc/init.matebookego.cfg`, while the original HDF manager's service definition and dynamic dependencies exist. 004 adds only this board configuration:

```json
{"import":["/vendor/etc/init/hdf_devmgr.cfg"]}
```

The file is created in a RAM-backed upper directory and presented through a read-only vendor overlay before the existing hardware fstab bind. There are no replacement service definitions, added jobs, changed UIDs/GIDs, changed critical-service rules, fake hardware nodes, or imported Kirin-specific frequency/sysfs jobs. All commercial lower images remain immutable. The original HDF executable and libraries are retained; no SDK userland is added.

The 002 volatile RenderService log directory and corrected 003 passive diagnostics remain unchanged. The known original L410 Mali Vulkan backend is not changed by this test; HDF publication alone cannot establish an FD690 desktop.

## Preparation verified

- Source test first failed without the board-import builder, then passed with the additive configuration, read-only overlay and retained 420-second outer deadline / 240-second target budget.
- Both static ARM64 executables compiled with warnings treated as errors. All five artifact hashes were validated by the installer.
- The 619,072-byte overlay has SHA256 `47c42b8835ba54f48bfcfbe520c969adbe61db81409ccd94d61334df588456de`. Exhaustive archive comparison proves only `init` and `native-target/bootstrap` differ from the commercial 001 base; commercial libraries are unchanged.
- Actual native non-PID1 execution guards refused both executables with exit 77. Installation preserved 98 existing EFI files, firmware entries, Ubuntu default, the manual GPU entry and the user-disabled screen-off timer. No partitions were formatted or images overwritten.

## Runtime status

The single bounded operational test ran on 2026-11-13 from 08:24:12 UTC to 08:28:44 UTC and returned to Ubuntu, boot ID `b2148fb3-f16c-43ad-9193-5d4eb015abb9`. Do not repeat this completed attempt. Entry: `commercial61-native-004.conf`; original kernel/DTB are shared from the MateBook 031 adaptation, with commercial 001 base initramfs plus the new small overlay.

The board overlay was applied, and init imported both the new board configuration and the existing original HDF definition. Kernel diagnostics record `ServiceStart started info hdf_devmgr(pid 86 uid 3044)`. Original hilog then records:

```text
01-01 08:00:07.144    86    86 I C02510/hdf_devmgr/hdf_remote_adapter: addsa 5100, success
```

The same original HDF manager PID remains visible throughout the available process samples. No `GetSaWrap SA:5100` failure appears in the recovered hilog. This verifies original-service execution and SA publication, not every HDF device or desktop readiness. The later exact-log interpretation in `hdf-publication-analysis.json` supersedes the deliberately unverified publication flag in the earlier process-only `minimal-startup-analysis.json`.

## Remaining blockers — not suppressed

- The original kernel HDF interfaces `dev_mgr` and `hdf_kevent` cannot be loaded. The HDF manager can publish its userspace SA despite those errors; publication must not be confused with hardware-driver availability.
- Setting `bootevent.hdf_devmgr.ready` is denied by the original parameter service. No parameter permissions or service identities were changed to hide this.
- Clients still cannot obtain `display_composer_service`. The original RenderService (PID 797) starts but its L410 Mali Vulkan backend continues to fail creating a kernel-driver context. FD690-compatible commercial graphics integration is not supplied by this one-file import.
- Foundation reports SceneBoard installation failure, error `8519727`. Its precise cause is not established here and no identity, signature or install checks were bypassed.

Therefore the minimal startup fixes are effective, but **a usable commercial desktop has not been obtained**. No physical touchpad/application acceptance or stable frame-rate claim is made.

## Evidence recovery and preservation

The initial original-partition `ro,noload` export encountered metadata checksum errors. The original partition was not repaired or journal-replayed. A separate sparse metadata clone was created with `e2image -r`; only that new clone underwent `e2fsck -E journal_only`. It occupies 600,666,112 bytes despite its 64 GiB apparent size. Recovered leaf extents then guided `O_RDONLY` reads of actual data blocks from the unchanged original device; zero-filled clone file data was not used.

The 63 clone-enumerated files are preserved under `runtime-evidence/`, with per-file and per-extent hashes. All 47 files obtainable from the initial read-only view match the recovered versions byte-for-byte. Its `Path.is_file()` scan silently omitted inaccessible entries, so the initial zero unreadable count is not a complete inventory. The recovered last phase is `phase-061.log`; later snapshots and complete target-teardown evidence are not claimed.

- Hilog: 12,959,901 bytes, SHA256 `6fd52341752d1b701a80b436b99c5814c8b81d6defaf495181bc1ebd5605aa98`, no null bytes.
- Diagnostic/fault stream: 618,072 bytes, SHA256 `120e482f9a270dfda31c0a503ca82ed09ca4c5e0ec582d14dc7aeffd731c6719`. Its last 1,466 bytes are zero and are not treated as valid diagnostic text; the earlier HDF import/start and Mali errors precede that tail.

Fresh post-return verification rehashed all four original commercial images: each still matches the ISO. Ubuntu remains current/default with no one-shot selection; the LAB partition is unmounted, firmware entries and the manual GPU entry remain intact, and the experimental screen-off timer remains disabled. Of 98 prior EFI files, 97 remain identical; only the boot-managed `loader/random-seed` rotated during boot and was not restored. No SDK userland substitution, installer execution, partition formatting or original-image writes occurred.

Software automatic return is retained, but cannot recover a fully wedged kernel. The specified commercial ISO identifies its userland as `6.0.0.110 API 20`; its identity is not relabelled or replaced with SDK 7.
