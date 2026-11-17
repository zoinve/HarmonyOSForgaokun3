# Original Policy Jack Input394

394 booted once and returned at2026-11-16T20:30:00.056665Z.
Run:commercial61-native-087-4ebb1cf2-847c-4664-a2f6-a770fe03d981.
Collector396 retrieved19 files readonly/noload. Final phase-180.log.
Analysis398 and post-return guard397 completed. Do not repeat394.

The original audio_server UID1041 has6 adapter mappings and one actual jack
descriptor (fd16,/dev/input/event10), observed twice with its OS_InputEvent
thread alive. The observer validated the descriptor's real kernel device name,
without reading input events. Config visibility and exact preload env both
equal1; AT_SECURE is0 as observed, not modified. Original credentials and checks
remain unchanged. This establishes actual policy-to-jack input connectivity,
NOT physical plug/unplug notification, UI route switching or headphone acoustics.

Hilog shows the three intentionally unused legacy event2..4 paths rejected with
ENOENT, while the original input thread remains alive on the real jack. The old
h2w-open error is absent, but initial-state success is NOT inferred from absence
of an error. No AUDIO376_STATE/INPUT trace records were captured: its placeholder
lies on the readonly vendor overlay.401 binds only this private diagnostic file
from a separate RAM source, retaining the readonly vendor and service permissions.

Speaker regression passed:361920,190080,198720 accepted frames;0,10402,11037
nonzero frames; total21439 nonzero actual ALSA frames, no operation errors.
Original public renderer completed pause/resume and timestamps advanced. Broker
exit was normal. Actual acoustic output remains unverified; jack state was0.
Bluetooth enabled and real advertising counters reached at least2560 packets,
not distinct devices. Physical touch contacts remain zero.120Hz unchanged.

397 verified Ubuntu current/default, absent oneshot, enabled/active screen-off
timer, lab identity and unmounted state. Desktop173,data165/197 and original
images remain protected. No disk suites or microphone recording ran.
Compression392 saved117949362 bytes from15 completed378/385 logs.391 removed
only unreferenced retired set378.img,3246721 bytes. Read old logs with226 open_log.
