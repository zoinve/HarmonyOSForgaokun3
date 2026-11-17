# Duplex420 Progress And Unconfirmed Return

Date:2026-11-17, Asia/Shanghai. Full basic-driver goal remains active/incomplete.
Order remains Bluetooth, physical multitouch, audio, then real120Hz.

## Implementation And Local Evidence

Added417 socket fixtures for real payload copying, partial-error data without
padded tails, truncated-payload rejection without modifying the caller buffer,
route mismatch rejection, S16/S32 conversion, mute closing the stream, and
singleton/unsupported-pin handling. Added419 ALSA doubles for partial reads,
EAGAIN/wait/EIO, oversized returns, counter overflow, cancellation, capture
position bounds, two-worker capacity and bounded shutdown with incomplete
configs.418 runs416/417/419 under GCC address/undefined sanitizers. All passed.
415 ARM64 backend and official-header/no-undefined VDI compilation also passed.
No fixture loads the real ALSA library or samples a physical microphone.

Fixed GCC misleading-indentation diagnostics in413. A subsequent source review
found query errors retained dead sockets. The working413 now invalidates failed
connections and position state;417 verifies failed start cleanup followed by a
successful new connection. Sanitizers and415 compilation passed after this fix.
IMPORTANT: this latter recovery fix is NOT in the frozen420 deployed artifacts.
Do not overwrite420 or retroactively claim it contains that fix.

## Target420

420 builds from401 jack/config/trace integration and keeps the original public
renderer350, original service credentials and authentication, BLE and passive
touch observers. It adds shared-card capture support with actual-read accounting,
Mic PCM3 / Headset PCM2, and two bounded server workers. The packaged real ALSA
library exports snd_pcm_readi. It adds no deliberate ambient recording probe.

421 installation passed essential identity/default/timer/transfer checks.
Desktop173, data165/197 and original images were not written.401's entry was
archived/retired; entries173/420 remain.401's standalone ESP overlay has NOT
been deleted. Ubuntu stays the persistent default; screen-off stays enabled.
No disk hash/fsck/tree suites or full data clone ran.

Exactly one boot was requested at2026-11-17 05:02:57 Asia/Shanghai
(2026-11-16T21:02:57.010962Z), from Ubuntu boot
f7327ae6-13b0-4a74-b03c-6a7ab55b5f10. No second boot was requested.
The423 watcher ran its1100-second observation window and exited1 with an
observation-expired message. SSH probes failed; a direct probe reported
connection reset before key exchange. Return to Ubuntu and the actual target
OS state remain UNKNOWN, not disproven merely by an SSH error. No runtime
playback, capture, worker, Bluetooth or touch result can yet be claimed for420.
No live execution session remains at this handoff.

## Resume Without Repeating The Experiment

First inspect current target connectivity and the existing420 attempt.
Do NOT boot420 again or install another candidate merely because observation
expired. After authenticated access returns, run422 observe for that same
attempt,424 essential return guard, and422 retrieve UNDER WSL. Retrieval must
exclude all prior runs through401.425 analyzes the last cumulative phase, not
an assumed phase number; actual capture metadata is separate from acoustics.

427 log compression and428 unreferenced-set401 cleanup are prepared but NOT
executed. Run cleanup only after actual evidence supports retiring that fallback,
preserving all currently referenced boot dependencies. No remote cleanup or
runtime log retrieval was possible during this turn. Do not recreate original.tar.

Pending acceptance is unchanged: Bluetooth pairing/reconnect/low-power, physical
multi-contact delivery and app gestures, speaker/headphone acoustics and hotplug,
real microphone capture/duplex, and supported panel modes/actual120Hz timing.
