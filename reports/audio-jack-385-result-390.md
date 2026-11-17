# Jack Detector385: Playback Retained, Adapter Not Loaded

385 booted once and returned at2026-11-16T20:21:00.589220Z.
Run: commercial61-native-087-4744ef95-3403-4b94-80f0-65963adb3e08.
Collector387 retrieved19 files readonly/noload. Final phase-180.log.
Analysis389 and post-return guard388 completed. Do not repeat385.

Original audio_server UID1041 and OS_InputEvent thread were observed, but
adapter_maps=0, real_jack_fds=0; no adapter state/input trace exists. This
contradicts jack-integration success, despite the library/config binding log.
Original hilog still reports absent h2w state. No headphone acceptance is claimed.

Runtime source places radio261_bind (including the early config mount) before
commercial_profile005 builds the system overlay.394 moves the modified config
into that final overlay and adds readonly observations of actual service config,
exact adapter-only preload env and AT_SECURE. No loader/security flag is changed.
The adapter code tested in377 is unchanged; original service path, UID/GID,
capabilities, permission list, token/authentication and sandbox stay unchanged.

Playback regression passed through original public API/services/VDI/real ALSA:
three speaker sessions accepted352320,191040,196800 frames, with0,10402,11053
nonzero frames. Total21455 nonzero frames, no operation errors. Pause/resume
advanced position and the broker stopped normally. Acoustic output unverified.
Bluetooth enabled and advertising packet counters reached at least2368, not
distinct devices. Touch had zero contacts; physical gestures remain unverified.

Guard388 verified Ubuntu current/default, absent oneshot, enabled/active screenoff
timer and expected unmounted lab partition. Desktop173, data165/197 and original
images remain preserved. No disk hash/fsck/tree suite or ambient recording ran.

All three references were consulted: L410 audio VDI has a no-op observer; Linux
compatibility asound.conf routes Linux audio toward Harmony through FIFO/Pulse,
not this physical ALSA backend; HarmonyMac ed213a0 enables original audio_host
but explicitly leaves ALSA/hardware unqualified. None supplies a proven Gaokun
jack implementation. Do not copy its extra capabilities or sandbox changes.
