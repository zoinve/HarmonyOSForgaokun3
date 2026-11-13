# Native original-service trial 001 — preboot review

This is a new operational experiment, not a rerun of native trial 012 or the numbered QEMU trials.

## Candidate and isolation

- Native Freedreno/MSM bundle 001; original SDK system/vendor/sys_prod images remain read-only and hash-checked.
- Original init runs as PID 1 in a new PID/mount/network namespace in a separate native boot. Original service identities and platform libc++ are unchanged.
- Writable data is a RAM-backed 512 MiB ext4 image; graphics and board configuration overlays are RAM-only. No emulator configuration or synthetic boot-complete parameters are imported.
- Original-service observation is bounded at 70 seconds; the outer init has a best-effort 180-second reboot deadline. A kernel hard lock remains outside this protection.
- Target SELinux remains supported and is explicitly permissive; Ubuntu's LSM configuration is not changed.

## Installation evidence

`native-original-graphics-boot-001/install-result.json` records the counted entry and 73,035,776 bytes of remaining ESP space. Only two unreferenced, byte-identical obsolete kernel cache files were deleted (`harmony-native-diag-009/linux` and `harmony-native-diag-010/linux`). The identical retained 015 kernel, original build products, historical initrds and logs remain. All other 80 prior EFI files and firmware boot entries were verified unchanged.

The persistent default remains Ubuntu. The new entry has one attempt and does not become the persistent default.

## Verification and preparation corrections

- Nine candidate artifacts passed read-only hash checks; the two native non-PID-1 guard refusals are recorded in `stage-result.json`.
- No WSL qemu-aarch64 user emulator is installed; emulated guard checks are explicitly reported as not run.
- The first preparation selected the one-shot entry but stopped **before reboot** because this systemd-boot version prints `OneShot Entry`, not the script's expected `One-shot Entry`. Its remote marker prevented repeating preparation. A second invocation was correctly refused by that marker.
- Preserved both rejected preparation outputs. The collector's findmnt parsing was also made whitespace-independent; this was a preventive correction, not the cause of the first preparation failure.
- The explicit `--resume-prepared` path validates the same preboot ID, unchanged entry text and the already-selected one-shot entry; it does not select another entry or repeat a completed boot.

Runtime outcomes must be taken from the subsequently collected raw snapshots, not inferred from this review or installation success. Desktop, service readiness and successful scanout are not established by preboot checks.
