# Native 078: real Dock readiness does not prevent guide relaunch

## Experiment and preservation

Exactly one boot, commercial61-native-078-fa16f0c9-4d70-4082-af81-3f6b79c28895,
2026-11-15 03:05:22 to 03:09:04 UTC. All 73 recovered file hashes matched,
without partition journal replay. Target timeout and TARGET_EXIT records were
recovered. Returned Ubuntu boot ID 4bc6d00b-1a66-4da5-80b3-d7887c41e700.

Post-return verification passes Ubuntu current/default, firmware, original four
images, enabled/active screen-off timer, original manual entry and unmounted
LAB. 139 baseline EFI files are unchanged except normal loader/random-seed and
the hash-archived user-authorized removal of entry 076. Experimental entry files
are 077/078; shared payloads remain intact.

Seven script-control scenarios, archive admission, fault-snapshot rejection
fixtures and input parser whitespace/marker tests passed. Native runtime does
not establish desktop success merely because those tests passed.

## Startup sequence and decisive counterexample

The diagnostic reads PID 4216's original HiLog Dock completion at 85.023 seconds,
rechecks that PID after two seconds and calls the unchanged original aa command.
Its snapshot explicitly reports force stop process successfully; at 90.81 s
the guide pidof is absent and SceneBoard PID 4216 is present. Focus is desktop
window 7, but the old guide window is still listed in the early WMS dump.

Unlike 077, this recovered log contains no THREAD_BLOCK_6S entry and only one
RegisterRootSceneSession for PID 4216. Nevertheless the same SceneBoard process
actively relaunches OOBE:

- interactive-hilog030.log:294633, 90.980 s:
  BaseOobeManager: sessionExceptionCallback is called.
- 294636, 90.981 s: BaseOobeManager: start oobe again.
- 294637: BaseOobeManager: start oobe ability.
- 296530, 92.502 s: same PID calls StartUIAbilityBySCB for the guide.
- 296615, 92.509 s: original appspawn starts the guide again.

This disproves the hypothesis that avoiding a SceneBoard restart or waiting for
Dock completion alone can make the guide dismissal persistent. The earlier
077 freeze evidence remains authentic but is not the sole relaunch mechanism.
Original OOBE manager reports provisioned 0 and user setup incomplete; neither
value was modified. Do not forge these records, bypass verification, disable
the callback, or claim commercial activation.

## Pixels and interaction

Both complete captures validate at source 2560x1600 / output 1600x2560 with zero
rotation differences. Before-input source PPM SHA256:
d9988952678f434f33c03cad720b57de591a4b5296b39e81bf20cc1c9b99f0df.
After-input source PPM SHA256:
a4728707e7888bf7bef27b626eea0180a09c981f02895821e68448316e23ee69.
11755 source pixels differ. Local OCR recognizes no text in either capture;
absence of OCR text is not absence of OOBE or proof of a desktop. Direct visual
inspection is unavailable because this model channel rejects image inputs.

Corrected input correlation verifies event6 LEFTMETA writes 48/48 bytes, one
matching physical keyboard event pair, and the same live SceneBoard's down/up
processing at 132.474 / 132.548 s. This proves framework delivery, not a visible
desktop action. The original bootstrap's marker intentionally remains 075.

Public trace prefix has 110 frame records and 5481 codec SendFrame errors.
Do not infer successful decoding or stream EOF. All desktop, interaction,
persistent-dismissal and activation success claims remain unproven.

Next work: inspect genuine OOBE-supported skip/exit behavior and its remaining
dependencies, keeping original authentication and service lifecycle intact.
Do not rerun this completed numbered boot or keep repeating successful kills
as though a single absent-PID sample established persistent dismissal.
