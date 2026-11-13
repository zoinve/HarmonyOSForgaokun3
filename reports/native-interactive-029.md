# HarmonyOS 029: manual interactive entry, no harness auto reboot

Installed menu title: **HarmonyOS 029 - Interactive NO AUTO REBOOT (volatile data)**

Based on 027, retaining landscape display/touch DT, USB PHY/HID, native GPU and QCA Bluetooth transport changes. This does not resolve the outstanding Settings issue or stable-120-FPS target.

## Behavior

- After the initial bounded evidence snapshots, the diagnostic parent waits indefinitely for original init. It no longer kills the target namespace after 70 seconds.
- Removed the 180-second physical reboot child and all physical `reboot()` calls in the diagnostic parent. If the target exits, the parent records that result and stops rather than rebooting/restarting it.
- Entry uses `panic=0`, disabling timed kernel-panic reboot. This is not a promise that firmware/hardware faults can never reset the machine; no unrelated hardware watchdog or service security checks were removed.
- Removed automatic touch-swipe and Meta+I injection. Unlock and interact manually.
- Ordinary uncounted menu entry, not a `+1` short-trial entry. Ubuntu remains the default; no one-shot selection or reboot was requested.

## Use and recovery

Reboot manually and choose the exact title above in the boot menu. Use the device normally; this build will not automatically return you to Ubuntu at the old observation deadline. If it hangs or you need to leave, use the physical power button/long press to power-cycle, then boot Ubuntu.

**Data is still a volatile 3-GiB RAM-backed filesystem. Apps/settings/session data are lost on power-off or reboot.** Original system/vendor/sys_prod images remain read-only; this is not a persistent installation. Crash files produced after the bounded initial export are not automatically saved when power is cut. No indefinite log-to-disk loop was added.

## Verification and preservation

Build passed static GNU/OHOS compilation. Source checks confirm no diagnostic-parent reboot/deadline/target-kill path and no synthetic gestures. Nine artifacts pass SHA256 checks; both real native non-PID1 refusal guards return 77. Installed initrd and candidate-local DTB hashes verified independently. This new interactive candidate has **not** been booted or endurance-tested; initial inherited hardware functionality is based on 027, not a new runtime claim.

Initrd SHA256: `a81b2ac901e93cbe678fe8d1065266aea55bfe61aa6dc32d05759fc5434130bb`.

Only the unreferenced EFI cache `native-original-graphics-019/initrd.img` was reclaimed after byte-for-byte hash comparison with its retained original staged copy and journal creation. Original 019 files/logs remain. All other 86 existing EFI files, firmware entries and Ubuntu default were preserved. ESP free space is 92,078,080 bytes. Ubuntu automatic screen-off remains active.

Artifacts: WSL `/home/zoinve/harmony-virgl-883/native-original-graphics-boot-029`, staged device `/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-029`, evidence `reports/native-original-graphics-boot-029/`.
