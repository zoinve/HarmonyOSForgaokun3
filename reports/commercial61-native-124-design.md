# Cmdline-Corrected OOBE Seed 124

The 123 early failure occurred before original service startup: the required commercial opt-in was present in the installed entry but absent from the kernel's recorded command line. Do not weaken the original bootstrap admission test.

Candidate 124 reuses every byte of the 123 payloads and the same private SettingsData seed. It only changes the boot entry's initrd list. Walking the overlay list backwards identifies archives whose entire pathname set is shadowed by later retained archives. Remove those entry references, not the payload files. Merge the retained member/mode/content maps and require exact equality with the full 123 initrd before installation.

The list shrinks from 37 archives to 27; estimated EFI-stub command line is 1644 bytes, with an admission ceiling of 1800 below the arm64 2048-byte boundary. All original options, including both opt-ins, permissive SELinux and panic return, remain present. No executable or original image is changed.

The new entry references existing verified payloads, including `commercial61-native-123/initrd.img`. Record a new installation journal and entry; retain only experimental entries 123/124, archiving 121 outside the ESP first. Preserve Ubuntu as current/default, original manual entry, firmware and enabled/active screen-off timer. Run once with the existing bounded return; do not rerun numbered boots.

Acceptance requires original service logs for the prepared first-run state, OOBE lifecycle/process checks, full-resolution framebuffer evidence and actual interaction. Seed loading, absence of a guide process, or successful return alone is not desktop acceptance. This candidate does not modify or claim commercial activation.
