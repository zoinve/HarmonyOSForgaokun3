# 032 — native touchpad cursor candidate

Installed manual entry: **HarmonyOS 032 - Touchpad cursor - NO AUTO REBOOT**. Not selected or booted automatically. Physical cursor/click behavior is **not yet verified**. Status-bar clipping is **not fixed** by this candidate.

## Evidence and change

The retained 031 physical-input run proves that the USB touchpad registers with MMI and sends motion to Settings. The SDK's actual cursor adapter uses an emulator implementation: the audited DrawPointer and SetPointerLocation vtable slots are bare returns. Hardware-cursor support is false. This identifies missing native cursor drawing, not a missing touchpad device; it does not establish whether every physical click or gesture works.

032 wraps the original factory and preserves its object, two vtable headers and all 59 original method slots except the three bridged drawing/location/visibility slots. Those three still delegate to the original implementation. The actual MMI coordinates and original visibility state are published through a 64-byte state file. No keys, clicks, motion or identities are synthesized. Original cursor-surface reporting remains unchanged: the scanout backend does not claim to create a RenderService surface.

The original adapter is retained as `libcursor_drawing_adapter032.z.so`, SHA256 `03e64bcecc882791855ec26840cfbfc8c4763e40e0e1612a677fd0d52b335d3e`. The wrapper checks the pinned factory and slot offsets at runtime; on an ABI mismatch it returns the original object without replacing its vtable. Build/archive verification checks the original bytes and both replacement libraries.

The composer paints a high-contrast default arrow into its back buffer, with the same clockwise landscape-to-panel transform as the existing desktop. A private clean background permits erase and idle movement without reading a released client buffer. A dedicated worker uses the existing state mutex, DMA ownership transitions, pending-flip wait and KMS page flips; it never writes the front buffer or fabricates vblank callbacks. This implements a default arrow, not the complete collection of cursor styles or a new gesture recognizer.

## Permissions and preservation

The target-only `/data/native-cursor032.state` is created before service startup, owner 6696, group 1003, mode 0640. Retained real process status establishes MMI UID 6696 and composer_host UID/GID 3036 with supplementary groups 1003 and 3061. The composer receives read-only mapping; MMI receives read/write mapping. Both validate regular-file type, exact size, ownership, permissions and link count. Sequence-stamped atomic fields reject in-progress snapshots. Original service credentials and SELinux policy loading remain unchanged; the target retains authorized permissive mode.

The initial uninstalled compilation in `native-cursor-032` used the wrong reader group. It is retained as build history, not deployed. The installed archive embeds only the corrected `native-cursor-032-r2` libraries, whose group check is 1003.

032 shares the independently verified 031 Binder kernel and touch DTB, and adds only its own initrd and loader entry. It does not overwrite 030/031 or delete EFI files. All 94 pre-existing EFI files, firmware entries, Ubuntu default and automatic screen-off timer were verified unchanged. EFI free space is 41,005,056 bytes; the installer retains a 32 MiB reserve because it adds no second kernel/DTB copy. The LAB partition is unmounted; original images and numbered evidence were not repaired or replayed.

Initrd SHA256: `78049c130b3ab1dcd8f29d192b168bed3681d16a8aa9c298e6b548987e51f8ad`.

## Verification and limits

- Host pixel/state tests pass under ASan/UBSan: rotation, clipping, padding, hide/erase, screen isolation, malformed buffers, incomplete/invalid state snapshots.
- A host ABI-shaped fixture checks forwarding and published coordinates/visibility. It is not a real SDK or physical-input runtime test.
- Both AArch64 libraries link without undefined symbols or compiler warnings. Nine boot artifact hashes and the embedded original/bridge/composer hashes pass verification.
- Two actual native non-PID1 execution guards reject startup, exit 77. Installation hashes and preservation checks independently pass.
- Inline review checked the pinned ABI boundary, actual composer credentials, owned background lifetime, mutex/worker shutdown and back-buffer DMA/flip ordering. No independent-agent review was used.
- Real 032 service startup, dynamic adapter loading, visible motion, tap/physical click, scrolling and idle movement remain pending. Stable 120 FPS remains unmet; this change does not remove the existing CPU rotation cost.
- Desktop/RS logical resolution remains 2560×1600. Physical 1600×2560 scanout is intentional rotation, not proof of a resolution bug. A full-screen photo is still needed to distinguish status-bar clipping, layout/orientation and missing status items.

## Manual acceptance

Select 032; move one finger while the desktop is idle, tap and physically click a target, then test two-finger scrolling. Check arrow placement at all four corners and that touching the screen hides the arrow without trails. If it fails, wait at least 15 seconds before returning to Ubuntu. Capture a full-screen photo showing the incomplete status bar. The new run directory is `native-interactive-032-<bootuuid>`; bounded original capture filenames deliberately remain `interactive-hilog030.log` and `interactive-faults030.log`.

See `native-original-graphics-boot-032/installation-final-verification.json`, `archive-cursor-verification.json`, and `native-touchpad-statusbar-032/remote-hash-verification-restored.json` for evidence.
