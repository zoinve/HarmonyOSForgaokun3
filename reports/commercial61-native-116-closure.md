# OOBE 116: initial query no longer stalls; original guide recovery remains

Exactly one completed bounded boot. Do not rerun 116 or overwrite its evidence.
Start: 2026-11-15T18:04:33.521136+00:00.
Ubuntu return: 2026-11-15T18:08:18.367206+00:00.
Run: commercial61-native-087-13eefda1-d895-49db-bbbc-468343e0c5e9.
Returned Ubuntu boot ID: 0f316a4d-80f7-4c2c-8815-bcfe8f20ce39.
Final phase-120.log records target_timeout=1 and target PID 438 exit status 9.

## Checkpoint and query outcome

The new gate observes current original CollaborationFwk PID 1074's callback
success log at local 2026-11-16 02:06:08.421. The exported event matches the
hash-verified raw HiLog exactly. Gate uptime advances from 50.39 to 67.10.
There are no gate refusals. This event remains a selected checkpoint, not a
claim of complete collaboration readiness.

Original appspawn creates SceneBoard PID 6006 at 02:06:08.649, after that
checkpoint. Only one SceneBoard creation is observed in the captured log.
Its synchronous trusted-device query starts at 02:06:19.419 and ends at
02:06:19.433: 14 ms. At the four uptime samples 90/110/130/145, SceneBoard
remains PID 6006. Unlike 114, no SceneBoard freeze-kill/replacement is observed.
The candidate therefore removes the observed initial stall in this run;
this is not a broader stability guarantee or proof of full memory-service repair.

## OOBE still recovers independently

The reference script retains one force-stop and no second SceneBoard start.
Original lifecycle records, all local 2026-11-16:

- 02:06:14.278: guide PID 7406 created.
- 02:06:24.519: guide PID 7406 exits with code 0; aa reports force-stop success.
- 02:06:24.522: PID 6006 WMS records the guide session exception.
- 02:06:24.531: the same PID 6006 executes sessionExceptionCallback and start oobe again.
- 02:06:24.600: original appspawn creates replacement guide PID 8973.

The callback/restart is 9 ms after the session exception and 12 ms after the
force-stop success timestamp. At every 90/110/130/145 sample, guide PID 8973
owns focus window 73. Thus avoiding the initial desktop freeze is not enough
to make reference force-stop persistent. Repeating kills is not a fix.

## Pixels and interaction

Both original source frames are complete 2560x1600 captures, with complete
1600x2560 rotated output. Rotation comparison has zero differing pixels.
Capture times: 120.005557 and 140.013904 seconds.
Source PPM SHA256 values:

- eb08cb490a59634662731635255d97c20483684d74c778a6a2456b5d7b6ddcdf
- 59d52223b6d23cdcc1f139799b44bf0bfb2c54671dff0a464b5a8f43749d9e75

There are 9766 changed source pixels. OCR is empty on the first and reports
Welcome on the second; neither establishes desktop state. A current view_image
attempt rejected the first source PNG because this model does not support
image inputs. No direct visual inspection is claimed.

The exact event6 keyboard writer and original SceneBoard PreLogoKeyEvent
down/up records prove framework delivery to PID 6006, not visible desktop
interaction. Stable interactive desktop and activation remain unverified.

## Preservation

136 retrieved files match remote hashes. Read-only noload retrieval finished,
and LAB is unmounted. HiLog SHA256:
8db84fd05182d3734158f59503a3c82313edba2617431c5491f5cefc86bdd166.
The credential audit passed 136 files / 379143883 bytes with no WPA PSK export.

Ubuntu is current/default, screen-off timer enabled/active, manual entry
retained, firmware and all four original image hashes unchanged. 163 prior
EFI files remain unchanged, apart from normal random seed and hash-archived
authorized removal of entry 109. Retention archive:
boot-entry-retention-20261115T180422020417Z.
Current experimental entries: 114 and 116; shared payloads retained.
Installed 116 overlay SHA256:
aad15f0c9a11f39a22a88cb0e936c9014399c332a99e5ee68528b8c9ad07291e.

Eight gate tests, three isolation guards, full overlay reconstruction and five
query-parser tests passed. Original services, identity, tokens, trust checks,
setup state, binary bytes, kernel, watchdog and recovery remain unchanged.

## Next boundary

Retain the observed useful startup-order change. Investigate the original
BaseOobeManager recovery condition and reference runtime configuration/state
without fabricating user_setup_complete, activation, trust, or service success.
The same supplied image is retained. Do not substitute a different desktop,
disable original recovery, broaden into kernel migration, or replay 116.
The full stable interactive native desktop goal remains active and unachieved.
