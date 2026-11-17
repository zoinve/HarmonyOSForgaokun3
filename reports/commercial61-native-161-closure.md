# Native 161: inherited-FD bind is the first failing operation

One bounded boot completed: commercial61-native-087-f6c2ce82-482f-407e-91b2-8b158c7c2841.
Start 2026-11-16 06:20:35 UTC, Ubuntu return 06:24:42 UTC.
No authenticated SSH connection occurred and no Settings/driver repair is claimed.

The 538-byte overlay and staged helper were loaded with both SHA-256 checks and
both inherited regular log FDs present. Root verification passed. The first log
bind failed before remount/statvfs or key copy:

- phase-172.log 92238: LIVE161_LOADER_READY, source/RAM hashes and FDs verified.
- 92239: original init root verified.
- 92240: LIVE161_STORAGE_REFUSED item=1 stage=5 errno=22.
- 92262: helper exit 93, namespace reaped.
- 313415: original supervisor reaped with state 23808 (exit 93).

All 190 retrieved files matched remote hashes. Post-return verification preserved
all four original image hashes, Ubuntu current/default, firmware, active screen-off
timer, unmounted LAB partition and 179 prior EFI files, except normal random seed
and archived authorized removal of entry 158. Latest entries are 159/161; no shared
payloads were removed. Ubuntu boot ID: 61a77587-105e-4312-8805-a9b057e63df5.

The next isolated fixture corrects an important fidelity gap in fixture 160:
real native logs are opened before clone(CLONE_NEWNS), whereas 160 opened its
synthetic source after unshare. Do not infer key failure or change permissions.
Original MMI still holds touch and storage modules remain live; physical input,
original USB-service acceptance and a full debugger remain unverified.
