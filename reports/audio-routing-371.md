# Audio Routing365 Progress

Date: 2026-11-17, Asia/Shanghai. Driver goal remains incomplete.
Order: Bluetooth, multitouch, audio, then120Hz. No repeat365 boot.

## Implementation And Tests

Protocol315 version2 carries an explicit route in unchanged24/72-byte structs.
Server316 selects real UCM Speaker/PCM1 or Headphones/PCM0. Headphones require
an actual readonly CARD-interface Headphone Jack boolean before any activation.
Absent or unknown jack fails without speaker fallback. Cleanup disables the
exact enabled UCM device. Capture remains unsupported, not silent capture.

VDI363 maps speaker/headphone/headset output pins, rejects unsupported routes,
limits the hardware render to one instance, and preserves only confirmed played
frames across a route switch. Failed switching leaves the requested route
stopped, without falling back to speakers. Reply route must match before bytes
are acknowledged. Original services, permissions and credentials are unchanged.

Tests364 passed official-header/platform and ARM64 builds, sanitizers, jack
guards, correct PCM selection, cleanup, invalid protocol/routes and singleton
handling. Lifecycle tests373/374 passed close/open failure and mismatched-route
reply checks. Fixtures establish local behavior, not physical headphone success.

## Actual365 Evidence

Run: commercial61-native-087-bd317498-86ec-430f-b40b-0a78235502f1.
Returned at2026-11-16T19:50:40.741272Z (2026-11-17 03:50:40 China).
Final cumulative log: phase-180.log. Collector367 retrieved19 files.
Analysis: commercial61-native-365/audio-analysis-370.json.

Three actual Speaker/PCM1 sessions accepted368640,190080,197760 frames.
Their nonzero frame counts were0,10402,11053, with peaks0,4,5 and no operation
errors. Total21455 nonzero frames reached actual ALSA through original services.
The public renderer completed with no API failures, including pause/resume.
Presented positions advanced37392 to78672; both snapshots had zero underflows.
The broker stopped normally, with no transport termination.

All three readonly jack observations were0, consistent with inventory362.
No target headphone PCM was opened. Neither acoustic output nor physical
headphone output is accepted by these results.

Bluetooth enabled again; real advertising-report counters reached at least2624.
These are packets, not distinct devices. Pairing/reconnect remains unverified.
Touch observation had zero frames/contacts; physical gestures remain unverified.

Guard369 verified the returned Ubuntu boot ID, persistent default, absent
oneshot, enabled/active screen-off timer and expected unmounted lab partition.
Desktop173, data165/197 and original images remain protected. No disk suites ran.

## Follow-Up And Storage

Automatic jack notification is not implemented. The pinned original VDI headers
define RegExtraParamObserver and ParamCallback, but not a headset event payload.
The L410 reference a_observer discards its callback and returns success; this
is not a working notification implementation and must not be copied as one.
Upstream source lookup this turn was unsuccessful (API rate limit and missing
raw paths); no guessed event or callback payload was added.

Compression372 losslessly compressed11 completed365 logs:128633559 bytes to
11360248 bytes, saving117273311 bytes. All decompressed hashes verified.
Read historical evidence with226 open_log; do not recreate raw duplicates.

Pending: authenticated Bluetooth peer/UI acceptance, physical multitouch,
acoustic output, real headphone switching and jack notifications, microphone,
broader audio controls, then supported panel modes and real120Hz timing.
No microphone recording, reboot or display mode change occurred this turn.
Future retrieval exclusions include365 as well as all prior completed runs.
