# Native 159 closure: path/address gates pass, pre-SSH storage gate fails

One bounded operational boot was completed, never repeated. Boot run:
commercial61-native-087-4f3275a0-8d96-4344-b652-46410b56877a.
Start 2026-11-16 05:53:48 UTC, Ubuntu return 05:57:55 UTC.

## Actual outcome

The original-init root guard now passes. The worker subsequently passed its
network/PID namespace check, current WLAN address selection, exclusive dynamic
sshd configuration generation and device-bound discovery socket creation.
It then exited 93 at the combined read-only-log-bind/key-copy gate, before any
SSH server or UDP reply worker was started. Exact failing substep and errno are
not recorded in this candidate and must not be guessed.

Evidence in runtime-evidence/raw/phase-172.log:
- 1651: LIVE159_LOAD status=0.
- 88817/88819: supervisor 3995, original target 495; anchored root verified.
- 88908: LIVE159_END status=93 namespace_reaped=1.
- 298797: supervisor reaped with state 23808 (exit 93).

The client completed its one observation window without authenticated connection.
live-runtime-analysis-159.json reports authenticated_native_readonly_channel_verified
false. This is not a Wi-Fi diagnosis, a full debugger, or a Settings/driver repair.

## Preservation and existing driver evidence

All 190 retrieved files matched their remote hashes. Return verification confirms:
Ubuntu current/default, no pending one-shot, unchanged firmware, all four original
image hashes unchanged, LAB partition unmounted, screen-off timer enabled/active,
178 prior EFI files unchanged except normal random-seed change and archived,
authorized removal of entry 157. Latest experimental entries are 158/159;
shared payloads were not removed. Ubuntu boot ID is
e5478e6f-48ca-4fc1-a0ee-aa170b3f8351.

Original MMI still holds the touchscreen, and storage modules remain live.
These do not prove physical input or original USB-service/UI acceptance.
Next step: reproduce the unchanged binding/key-copy functions in a separate,
bounded native Ubuntu mount/PID namespace, before another HarmonyOS boot.
The full basic-driver objective remains active.
