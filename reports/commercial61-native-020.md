# Commercial image 020 — reference-aligned SceneBoard startup

## Intent and reference

The objective remains the real commercial desktop, not merely an installed SceneBoard package or initialized GPU. Original 019 logs show real account 100 creation/key unlock followed by activation rollback because SceneBoard does not exist. The provided account-order script waits for account activation before attempting its desktop launch.

All three adaptation references were reviewed together. HarmonyMac's `ports/tests/native-desktop-start.sh` uses the normal Ability Manager `aa start` entry after service readiness. This candidate follows that entry, **not** the reference's later forced startup-guide termination. The L410-specific Mali graphics and identity compatibility preloads are not copied into this MateBook startup change.

## Bounded change

Only the volatile copy of `l410_account_first_boot_order_v1.sh` changes. It retains the original HUKS stability wait and stock Account Manager restart, removes the circular account-ready wait, and requires the original application-framework and bundle-scan readiness indicators before invoking:

```sh
/usr/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard -u 100
```

Preflight incorrectly inferred support for `-u` from strings in the original `aa` executable. The actual 020 execution proves that **this commercial `aa start` rejects that option**, even though it returns shell exit code 0. The command above is the historical failed attempt, not a recommended command. Normal Ability Manager authorization, application sandbox, seccomp, package checks, service credentials and authentication were not bypassed. No guide was force-stopped and no completion state was forged.

## Installation and acceptance

Source ordering/argv tests and transformation of the actual original script passed. The complete archive's byte/mode state equals the ordered 001 → 017 → 016 → 020 initramfs chain. The new 704,564-byte overlay has SHA256 `6c0876d6d7bada870c5c7b1c252544970577fcb148c23f882d4f58d4cdc62695`.

Installation retained all 118 existing EFI files, original image hashes, firmware, Ubuntu default, the manual GPU entry and disabled screen-off timer. No files were deleted. The explicit reserve is now 29 MiB; 31,113,216 bytes remained. Existing memory admission, 8 GiB volatile data, 90-second target budget, independent 210-second deadline and bounded final flushing remain. Software deadlines do not guarantee recovery from kernel or hardware deadlocks.

## Actual result

The single attempt ran on 2026-11-13 from 12:55:35 to Ubuntu becoming reachable at 12:58:03 UTC. All 59 exported files matched their remote hashes; retrieval mounted the original evidence partition read-only with journal replay disabled, then unmounted it. The configured target termination is recorded. Network reachability alone is not proof of every teardown step.

The actual command was invoked at guest time 44.039 s. Its captured output at 44.171 s says `fail: unknown option.` and prints `aa start` usage without a user-ID option. The wrapper subsequently recorded `result=0`. This is command-line rejection, **not an accepted desktop launch**. The original SceneBoard package installed successfully, but no SceneBoard process was observed. All three actual 160×256 scanout captures remain black. Seccomp filter-name failures, SA 511 unsupported errors and ENOSPC errors were absent.

Post-return verification preserved the four original commercial image hashes, Ubuntu default, firmware, manual GPU entry and disabled/inactive custom screen-off timer. Before the separately authorized EFI cleanup, 117 of the 118 previous EFI files were unchanged; only the boot-managed random seed rotated. Subsequent intentional, backed-up deletion of unreferenced old EFI artifacts is recorded separately in `efi-unreferenced-cleanup-001.md`, not treated as a preservation failure.

**The commercial desktop has not been obtained.** The next correction must use the reference's ordinary `aa start` arguments, with no unsupported `-u` addition. Acceptance still requires the actual desktop process and real captured pixels, never a CLI exit code alone. Existing runtime logs and JSON evidence remain unchanged.
