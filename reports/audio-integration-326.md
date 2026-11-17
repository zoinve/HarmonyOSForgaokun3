# Audio Integration321

Date:2026-11-17, Asia/Shanghai. This follows real Bluetooth enablement297/306.
321 has been built, installed and booted once. Do not repeat this boot.
Runtime result is pending at report creation.

## Implementation

Official VDI1.0 headers are from OpenHarmony peripheral6.0 release commit
`8cd47d4bb09a4d160e8b713b2fbccf8d41e2025f`, path
`audio/interfaces/sound/v1_0`. These are the correct VDI types, distinct from
HDI5.0 IDL. The reference VDI compiles against them without guessed structs.

The original primary adapter is replaced only by a RAM read-only bind mount;
the original HDI/service configuration and UID3127 remain. The backend socket
is UID3127, mode0600, and is exposed through the original sandbox's existing
recursive vendor view. Client also checks broker UID0. No service privilege
or authentication changes were made.

`native-audio-server-316.c` uses real ALSA/UCM and the existing deployed
HUAWEI-matched profile, speaker PCM1. It accepts only48kHz stereo S16_LE on
the wire. Actual original audio_server requests48kHz stereo S32_LE, so the
VDI performs explicit S32-to-S16 conversion and correctly translates accepted
wire bytes to source bytes. Volume, gain, mute and stereo channel modes are
applied to samples. ALSA is the only playback clock; no synthetic pacing.

Each frame transaction receives actual accepted-byte accounting. Position
uses submitted frames minus real ALSA delay, with a monotonic timestamp
sampled beside the delay query. XRUN/errors are surfaced, not converted to
success. Drain and flush invoke real ALSA operations. Unsupported capture
returns an error and zero delivered bytes, not fabricated silence. Capture,
headphone routing and broader format/rate support remain work, not complete.

The host ALSA closure314 contains895 public system files,5386465 unpacked
bytes,1932410 transfer bytes. The archive was not retained after extraction.
No host audio route was changed and no microphone was recorded while obtaining
these assets. No reference SmartPA SKU initialization was executed.

## Tests And Acceptance

`audio-native-test-320.json` and323 record platform library/ARM64 server
compilation and sanitized local tests. Tests cover missing-backend failure,
unsupported capture, volume/gain range, S16/S32 conversion, partial writes,
EAGAIN, XRUN, invalid delay, drain and malformed handshake. Test doubles are
explicitly not hardware or original-service acceptance.

321 retains Bluetooth297 and touch monitor306. Its actual window remains360
seconds with120 seconds reserved for cleanup; boot title900 seconds is the
outer upper bound. Readiness of the listening socket does not prove PCM
initialization or audible output. Inspect AUDIO316_PCM_READY and AUDIO316_IO
alongside original audio_host/audio_server logs before claiming progress.

Desktop173, data165, original images, default Ubuntu boot and screen-off
timer are preserved. Only candidate197 is used by normal diagnostic boots.
No disk hashes, fsck or tree-comparison suite was rerun.

Retrieve with `collect-audio-321-324.py`; its exclusions include306. Next
retrieval must additionally exclude321. Working entries currently173/321.
