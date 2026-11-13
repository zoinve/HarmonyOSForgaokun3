# Diagnostic009: legacy Binder / initially enforcing native kernel

## Purpose and limits

Test profile003's real native kernel on the board with the established diagnostic module sequence, read-only identity helper, 180-second best-effort deadline and 30-second admission reserve. The only generated diagnostic-C change from008 is `/bin/native-identity-read-001` → `/bin/native-identity-read-002`.

Profile003 enables SELinux in the existing LSM list and uses traditional Binder devices instead of Binderfs. Its developer-enabled SELinux build **requires explicit `enforcing=1`** in any diagnostic entry. No policy is loaded by this diagnostic. Initial active/enforcing state is not equivalent to loaded-policy authorization or a secure HarmonyOS service boot.

No identity setters, permission grants, replacement manager, authentication/database modifications, SDK-image changes or downloads are added. This is Linux hardware/ABI diagnostics, not HarmonyOS.

## Verified offline evidence

- `reports/baremetal-diagnostic-init-009/result.json`: archive 24,527,376 bytes, SHA-256 `c249d700d67c14dbd3c97182a823c14ecd9dde3102a9ff9aae358576f20b1d4c`.
- Generated C SHA-256 `6ea7bf8d7302c51d70f09dc1e6932c223698c5edb81a51edd858ec5010f5326d`; init binary `91611c8116379cb5752e2a99c19475148e55df18f9b169d6a17e712731d9a4b0`.
- Native kernel SHA-256 `4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`; DTB `2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32`. Never substitute the QEMU console kernel.
- Independently verified all 620 parent archive records (bytes, modes, UID/GID) unchanged, exactly two added records (`init`, `bin/native-identity-read-002`), actual binary/helper/kernel/DTB hashes, and local/WSL manifest equality. See `independent-verification.json` in the same report directory.
- Helper SHA-256 `3aa3890222f8448ff1e8feef5e101f378e20449cebfd247a83c684b2e438dd31`; its real isolated-QEMU positive/opt-in-refusal cases and independent verification are recorded under `reports/baremetal-native-identity-qemu-047/`.
- Six targeted suites / 23 checks passed: diagnostic core, budget, budget integration, actual009 C snapshots, Ubuntu screen-off policy, immediate reconnect. See `reports/baremetal-diagnostic009-tests.txt`. This is not a repository-wide suite claim.
- All 152 preserved trial005 raw logs were checked locally/remotely before and after restoring only the lab partition's preparation flags to RW. See `reports/baremetal-lab-workspace-rw-006.json`.

## Reference and execution status

HarmonyMac is cross-checked for the relevant kernel/native-init principles, without transplanting Apple/VM settings or its software-only GPU assumptions. The second user-provided reference project has not been identified in restored records; `reports/reference-project-crosscheck-001.json` states this explicitly. No claim that both projects have been reviewed is made.

At this writing, the fresh assets are being staged only in the isolated lab workspace. No009 boot entry has been installed and no009 board boot has been requested. Real ARM64 non-PID1 refusal is checked during staging before any entry preparation. Subsequent preflight must use a fresh post-cleanup EFI baseline, preserve Ubuntu as the persistent default, retain automatic Ubuntu screen-off, and begin SSH observation immediately after any authorized reboot request.

Staging subsequently completed: all five actual ARM64 lab files match their recorded hashes/sizes, and both init and the helper refuse execution outside the diagnostic context with exit77. See `reports/baremetal-identity-diagnostic-009-staged.json`. Staging did not modify EFI entries or request a reboot.

## Subsequent entry preparation and trial006

Fresh `baremetal-boot-entry-preflight-006.json` verified the 13 original loader configurations exactly, no old on-disk diagnostic entries, no pending one-shot, the unchanged Ubuntu persistent default and enabled/active Ubuntu screen-off timer. Independent009 installation then verified all 73 pre-existing EFI files unchanged, unchanged firmware boot entries/default, exact native profile003 kernel and009 archive hashes, and explicit `enforcing=1` in the single-attempt entry. See `baremetal-boot-entry-installed-006.json`.

Trial006 was launched once with immediate bounded SSH observation and automatic raw-log collection after a changed boot ID running the expected Ubuntu kernel. At this update, no trial006 hardware result or successful return has yet been asserted. Initial SELinux enforcing-state checks without a loaded policy must not be represented as original-policy authorization or a HarmonyOS userspace boot.

The deadline is best-effort, not recovery from kernel hard locks or stalled synchronous filesystem operations. Earlier QEMU loaded-policy service evidence remains distinct from this policy-unloaded board diagnostic.
