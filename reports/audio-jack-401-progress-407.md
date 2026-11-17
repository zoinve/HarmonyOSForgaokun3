# Original-Service Jack Detection401

Date:2026-11-17, Asia/Shanghai. Full basic-driver goal remains active/incomplete.
Order remains Bluetooth, multitouch, audio, then120Hz. No repeat401 boot.

## Root Cause And Implementation

375 pinned original OpenHarmony detection sources at
aa89ed8302f8bccdf1eab0d32574c16d9ba58b5e and checked the supplied image's actual
policy library. Its legacy input detector opens only event1..4. Actual Harmony
365/394/401 places the physical headset jack at event10; Ubuntu used event4,
so host enumeration alone was misleading.

376 is a narrow open/fopen adapter loaded only by audio_server. It additionally
checks the calling DSO is exactly libaudio_policy_service.z.so. The original
event1 request dynamically discovers the actual Gaokun jack by kernel name,
character-device type and switch capabilities; it returns the real descriptor
with ordinary permissions. Legacy event2..4 are intentionally absent for this
detector, not globally renamed or hidden from MMI/other processes. No events
are generated, translated or injected. Actual original PNP code reads the fd.

The initial h2w-state fopen reads real EVIOCGSW state and returns a sealed,
readonly snapshot:0 unplugged,1 headset,2 headphones. Missing/unknown/inconsistent
readings remain errors, never fabricated unplugged state. No microphone data is
read.377 passed platform build, address/UB sanitizers, three state translations,
unknown/error guards and exact-callsite/passthrough interposition fixtures.

The sole original service-config delta is its adapter LD_PRELOAD env entry.
Path, UID/GID, capabilities, permission lists, token/authentication and sandbox
are unchanged. Original libc exports were checked for every required symbol.
394 places this config in the final system overlay, not its hidden lower.
401 changes only the private trace bind to permit bounded diagnostic writes;
the vendor overlay remains readonly and trace stays UID1041/mode0600.

## Actual401 Evidence

Run:commercial61-native-087-13268393-de84-4e45-8a18-1d062a867396.
Returned at2026-11-16T20:37:45.253718Z (2026-11-17 04:37:45 China).
Collector403 retrieved19 files readonly/noload; final cumulative phase-178.log,
NOT180. Structured result:commercial61-native-401/audio-analysis-405.json.

Original audio_server UID1041 has6 adapter mappings, one real event10 jack fd16
and a live OS_InputEvent thread, observed twice. Service-visible config and exact
preload env both equal1. AT_SECURE=0 was only observed, never altered.
AUDIO376_INPUT value10/errno0 confirms real-device open; AUDIO376_STATE
value0/errno0 confirms actual startup snapshot succeeded. The twice-observed
records replay the same bounded trace, not two independent physical events.
Independent readonly ALSA jack observations were also0. No headphones inserted.

Playback still goes through original public API/services/VDI into real speaker
PCM1:359040,191040,197760 accepted frames;0,10402,11053 nonzero frames. Total
21455 nonzero actual ALSA frames, no operation errors or transport termination.
Renderer completed21 callbacks,19148 source nonzero frames, zero invalid buffers
and no API failures. Pause/resume presented position advanced37392 to79632;
both snapshots had zero underflows. Broker stopped normally, forced0/status0.
Acoustic loudspeaker or headphone output is not independently verified.

Bluetooth enabled and actual advertising counters reached at least1856 packets,
not distinct devices. Touch monitor completed with zero contacts/frames/drops;
physical multitouch/app gestures remain unverified.120Hz is unchanged.

## Preservation And Next Work

404 checked the exact returned boot ID, Ubuntu current/default, absent oneshot,
enabled/active screen-off timer, expected lab identity and unmounted partition.
Desktop173,data165/197 and original images stay protected. Latest entries173/401.
No disk hash/fsck/tree suites or ambient recording ran; no full data clone made.
378 initialization failure,385 unloaded-adapter result and394 partial success
retain their own evidence/reports; none was rerun or relabelled as full success.

392/408 losslessly compressed completed378/385/394/401 logs, saving344937119
bytes total, with decompressed integrity checks. Read through226 open_log.
382/383/391/406/409 removed only unreferenced retired standalone overlays,
preserving every active reference and canonical local build.409 removed set394.

Still pending: real physical plug/unplug and original UI route switching,
headphone acoustics, microphone capture and broader audio controls; Bluetooth
pairing/reconnect/low-power; physical multitouch; then supported/real120Hz timing.
The existing UCM declares Headset capture PCM2 and Mic capture PCM3, but this is
configuration, not capture acceptance. Future duplex work must coordinate the
shared UCM verb/device lifecycle: current playback cleanup selects Inactive.
Do not independently deactivate it while another stream is using the card.

Future retrieval exclusions:235,253,262,266,276,285,294,297,306,321,331,341,353,
365,378,385,394,401. Keep360-second work/120-second cleanup reserve. Do not retry
unauthenticated root-aa ability launches or forge tokens to obtain UI acceptance.
