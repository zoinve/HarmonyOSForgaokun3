# Native identity/hardware diagnostic 008

This is **not HarmonyOS**. It pairs the rebuilt, identity-patched native kernel with its independently verified matching module inventory and the working 007 display/touch module plan. The only added diagnostic phase is an eight-second admitted identity read, using the existing 180-second best-effort deadline and 30-second reserve. Existing PID-1/kernel/opt-in/storage guards remain in place.

The helper reads task identities without setting them, verifies unsupported SPM commands return an error without altering the output, and creates a private **RAM-only** binderfs instance to check protocol 8, exact feature bits 5, fresh zero caller identity and reserved bytes. It closes its descriptors and unmounts before reporting success. It creates no persistent Binder service, assigns no token and modifies no permission store. Its success is not a transaction or desktop test.

## Evidence before the board trial

- QEMU 009 passed the exact helper with the real patched kernel, plus the retained raw synchronous/one-way/nested transaction checks and unmodified original SDK token/Connector checks. Independent verification checked all 17 RAM files, serial-log equality and test-kernel hash. The console-enabled test kernel differs from the native kernel only as already recorded in the test build; this is not board evidence.
- 24 targeted checks passed: core 5, budget 3, budget-entry 3, 008 snapshot harness 4, module/guard contract 1, screen-off policy 4 and reconnect 4. The actual driver-handler host harness also passed its four case groups. This is not a unified repository-suite claim.
- Actual MateBook ARM64 execution refused both the diagnostic init outside PID 1 and the helper outside the diagnostic kernel/opt-in, each returning 77 before device/mount changes.
- All 116 prior raw logs were locally and remotely verified before and after restoring the isolated lab filesystem's preparation flags.
- A fresh post-cleanup baseline verified all original 13 loader configurations, absence of old diagnostic configs, persistent Ubuntu default, empty one-shot and active screen-off timer.
- Installer 005 preserved all 70 pre-existing EFI files at installation, firmware entries and Ubuntu default; it installed only an independent one-attempt 008 entry and assets. The installer itself did not select or reboot.

## Immutable assets

| Asset | SHA-256 |
|---|---|
| Native kernel | `8ba8c0049c3608e3a72769897e718051c78addb4d73a29699714f2e49f576457` |
| Board DTB | `2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32` |
| Initramfs, 24,527,050 bytes | `58159556c88dc79ca32adf15aa386dd320e18403d33b32de9c7480705761d2fe` |
| Diagnostic init | `d687bb994d81943549654195c12bf8e9c56f9b1d7d6ce8137990adf366c2f592` |
| Read helper | `d27fc2a8a0f1a1644bd56028c3a0774879ead29b8a2befac206ea1f07f462e98` |

The complete inert parent archive is preserved entry-for-entry; only `/init` and `/bin/native-identity-read-001` are appended. Core source/header hashes remain unchanged. Staging, build, test and installer records are separate fresh numbered reports; previous archives and evidence were not overwritten.

Trial 005 has been launched separately and its outcome is pending at the time of this note. Inspect actual phase statuses, ABI output, DRM connector/mode and input registration before claiming board success. A changed boot ID or successful modprobe is insufficient. Kernel hardlock recovery remains unproven. Ubuntu screen-off covers Ubuntu, not firmware or diagnostic initialization, which may briefly illuminate the panel.
