# Original-Service Audio Playback353

Date:2026-11-17, Asia/Shanghai. Progress this turn: real nonzero playback and
pause/resume acceptance through the original audio services, not just PCM clocks.
The full basic-driver goal remains active and incomplete.

## Implementation And Local Tests

349 counts only stereo S16 frames actually accepted by snd_pcm_writei, after
the real return value and range check. It retains total accepted/nonzero frames,
absolute peak and operation-error counts, never sample contents or microphone
data. Flush does not erase its lifetime accepted-frame totals. Failed writes
cannot count unaccepted tail samples. Existing wire ABI is unchanged.

350 is a bounded public OH_AudioRenderer client, not a direct ALSA probe. It
uses normal48kHz stereo S16 music playback and original permission checks.
Each start has100ms silence followed by a200ms faded440Hz signal, source peak
256/32768, own-stream volume0.25; system-wide volume is untouched. It pauses
for3500ms before resuming and has a15-second process alarm.351 reuses verified
target namespaces/root, unchanged credentials, and a20-second parent bound.
No token is installed, forged or borrowed; no ambient audio is recorded.

The VDI now rejects non-speaker CreateRender and route requests rather than
claiming success while directing them to speakers. Headphone support is NOT
implemented by this guard and remains part of the unfinished audio goal.

352 passed official-header platform-library and ARM64 server builds, sanitizers,
missing-backend/partial-write/error/idle tests, new accepted-sample accounting
tests, speaker/unsupported-headphone route checks, bounded/faded renderer sample
generation, and platform compilation of350. These fixtures are not hardware
acceptance. The renderer's18 imported public OH_Audio symbols were separately
verified against the supplied image's actual/system/lib64/ndk/libohaudio.so.
Existing loader NDK inheritance is sufficient; no loader/service environment
or authentication configuration was changed. ABI evidence is in the353 build
directory's audio-renderer-abi.json (also listed in its artifact metadata).

## Actual353 Result

353 booted once and returned to Ubuntu at2026-11-16T19:29:57.613672Z
(2026-11-17 03:29:57 Asia/Shanghai). Do not repeat353.
Run:commercial61-native-087-f8d13375-1542-45ef-a2a5-e9cec2b6fee5.
Collector355 retrieved19 files. Final cumulative log is phase-180.log, NOT181.
Structured evidence: commercial61-native-353/audio-analysis-357.json.

Original services created the output and the actual ALSA speaker PCM opened.
Three completed PCM sessions report:

| Session | Accepted Frames | Nonzero Frames | Absolute Peak | Operation Errors |
| --- | ---: | ---: | ---: | ---: |
| Original startup stream |359040|0|0|0|
| Public renderer first run |191040|10402|4|0|
| Public renderer resumed run |197760|11053|5|0|

The original startup stream really is silent; prior PCM counting did not
establish playback of nonzero audio. The new public renderer's signal went
through original service mixing, VDI S32-to-S16 conversion and actual ALSA
writes. Nonzero output after original mixing is21455 frames in total. The
source/helper count need not equal the processed backend count; these are
different points in the audio processing pipeline, not copied counters.

All public API steps returned0. Helper completed with21 callbacks,19148 source
nonzero frames,0 invalid buffers and result0. First running snapshot reported
49038 frames written, presented position37392; resumed snapshot89160 frames
written, presented position78672. Timestamp/frame/underflow queries all
succeeded; both snapshots had0 underflows. This establishes original-service
playback plus a real3500ms pause/resume cycle, not acoustic loudspeaker output.
Audio broker ended normally:forced0/raw status0, no transport termination.

Bluetooth enabled again and real LE report counters reached at least2496.
Physical touch observation still had0 frames/0 concurrent contacts/0 drops;
no physical multitouch or app gesture acceptance is claimed.

## Preservation And Remaining Work

358 rechecked the returned boot ID, Ubuntu current/default entry, absent oneshot,
enabled/active screen-off timer, expected lab partition identity and unmounted
state. No disk hash/fsck/tree-comparison suite ran. Latest experiment entries
are173/353. Cleanup356 removed only unreferenced set331.img (3228116 bytes).
Desktop173, data165/197 and original installation images remain protected.
Compression360 saved117509984 bytes from11 completed353 logs using the existing
lossless integrity checks. Read compressed evidence through226:open_log.

Still pending: actual acoustic playback, implemented/validated headphone
routing and jack notification, microphone support, broader audio/volume/mute
acceptance, Bluetooth pairing/reconnection/low-power, physical multitouch/app
gestures and120Hz. Do not relabel unsupported capture or rejected headphone
routes as completed drivers. Keep120Hz unchanged until audio work advances.

Future retrieval exclusions:235,253,262,266,276,285,294,297,306,321,331,341,353.
Keep360-second work window/120-second cleanup reserve and numbered evidence.
No more unauthenticated root-aa page-launch retries:341 already proved denial.
