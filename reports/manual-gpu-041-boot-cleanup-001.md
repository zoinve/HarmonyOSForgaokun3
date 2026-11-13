# Manual GPU HarmonyOS entry and menu cleanup

User requested removal of old boot entries, one non-auto-exiting HarmonyOS entry, and waking the GNOME display. No reboot was requested or performed.

## Installed result

- Only HarmonyOS menu entry: `harmonyos-gpu-manual.conf`, title **HarmonyOS - GPU accelerated - MANUAL EXIT (no auto reboot)**.
- Uses unchanged 031 Binder-fixed kernel/DTB, unchanged 032 manual initramfs, and a 34,076-byte overlay containing **only** the previously runtime-verified 041 GPU composer. Overlay SHA256: `74e23840e0dfc57d94e23791dac8935b78905cc12e8be1fe6b17981c6312886d`.
- Archive verification proves `/init` and every other base member remain byte-identical to 032; that init has the indefinite child wait and no reboot/deadline code. The new entry retains `panic=0`. Simply removing the watchdog option from 041 was deliberately avoided because its deadline is compiled into init.
- Archived 16 old HarmonyOS entry files, including exhausted counted entries, to `/home/zoinve/.local/share/harmony-arm64-kvm-lab/manual-gpu-041-boot-cleanup-001/archived-entries`. Every backup was hash-verified before removing its original menu file. All kernel/initrd files and historical logs remain intact.
- All 90 other pre-existing EFI files, Ubuntu default, firmware entries, and unrelated Ubuntu/fastboot menu entries were unchanged. No one-shot selection was made. New combination was not boot-tested; its manual init and GPU composer were verified separately in earlier versions.

## GNOME display

GNOME's active local session is the GDM greeter (`c1`); no password bypass or automatic login was performed. Mutter `PowerSaveMode` was set to zero and read back successfully; actual panel brightness was 204.

The experiment timer `harmony-lab-screen-off-001.timer` was discovered to force the display off every ten seconds. Merely waking the screen was insufficient. It and its service were stopped **for this boot only**, then the screen was woken again. The timer remains enabled for the next boot. GNOME's normal idle/lock settings and persistent timer configuration were not modified. This final timer state supersedes the earlier intermediate verification that recorded it active.

## Evidence

`reports/manual-gpu-041-boot-cleanup-001/` contains the overlay manifest, installation stdout/stderr/result, independent post-installation verification, and final `gnome-screen-awake.json`. `test-manual-gpu-041-cleanup-001.py` passed archive/manual-init checks after the initial missing-builder failure. A test-only incorrect assumption about the bootstrap archive pathname was removed; the exhaustive unchanged-member comparison covers its real location without guessing it. Prior numbered operational experiments were not repeated.
