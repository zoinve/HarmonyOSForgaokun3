# Driver Progress

Updated2026-11-17, Asia/Shanghai. User order: Bluetooth, multitouch, audio,120Hz.

## Bluetooth297

The original service completed enablement using the real QCA controller.
The scoped broker recorded64 HCI commands and64 completions. Reset0c03,
version1001 and address-read1009 completed with status0. One completion for
opcode0c6d returned17; it is retained rather than translated to success.

Original hilog evidence, `commercial61-native-297/runtime-evidence/raw/interactive-hilog030.log`:

- Line128835: BTIF_dm_enable SUCCESS.
- Line128889: Bluetooth enable event completed.
- Line128912: BleAdapter OnEnable ret=1.
- Line129168: ClassicAdapter OnEnable ret=1.
- Line130487: bluetooth switch state is on.

The previous five POWER_ON failures are absent. The private adapter trace now
contains initialize, power-on, channel-open, and firmware-init successes.
This fixes the missing sandbox endpoint demonstrated in294; original
credentials, HDI, authentication and sandbox grants remain unchanged.

Residual: nearby discovery, pairing, reconnection and low-power behavior are
not verified. Vendor operations5,6,8 still return ENOTSUP and the original HDI
logs GET_LPM_TIMER failure. Enablement succeeded despite these unsupported
operations. Do not describe all Bluetooth features as complete.

Machine summary: `commercial61-native-297/radio-analysis-302.json`.

## Multitouch

The actual Himax device reports slots0 through9 and2559x1599 maximum
coordinates. Original MMI adds device2 successfully and holds its evdev node.
These are capability/attachment observations, not proof of app-level gestures.

Added `next-experiment/native-touch-monitor-303.c`: read-only120-second evdev
monitor, no grab, no event injection, no coordinate export. Parser self-tests
for two contacts, release, invalid slots and SYN_DROPPED invalidation passed
with address/undefined-behavior sanitizers. ARM64 static compilation passed.
See `touch-monitor-test-304.json`; that test did not run hardware.

Candidate306 retains297's Bluetooth runtime and adds the monitor. It has been
installed and booted once; retrieval is pending when this report is created.
Do not rerun306. A valid physical acceptance must require no observer error,
no dropped frames and at least two real concurrent contacts; app delivery is
separate. If no user touches occur, leave physical acceptance pending.

## Audio And Refresh Rate

No audio or120Hz acceptance yet. Read-only297 evidence shows a real
SC8280XP-HUAWEI-GAOKUN3 card appears after early initialization, with two
playback and two capture PCMs. Early `no soundcards` is not the final state.
Sound device nodes currently appear as root-owned0600. Original audio_host
registers its primary manager but also logs absent secondary driver libraries.
Determine the actual primary render path and backend before changing access
or libraries. The reference audio VDI includes fallback pacing/success when
its PCM socket is absent; do not import that as proof of real playback.

## Storage And Preservation

Losslessly compressed30 completed276/285/294 logs, saving378695987bytes.
Removed only10 retired, unreferenced ESP set overlays, freeing6807418bytes;
all active boot dependencies remain present. See `radio-log-compression-300.json`
and `unused-esp-overlays-cleanup-309.json`.

Desktop173, current candidate197 data, active165, original images, Ubuntu
default and screen-off timer remain protected. No disk-hash/fsck/tree suite
was rerun. No physical serial, UDID or authentication result was fabricated.

##306 Result And Next Audio Work

306 returned automatically to Ubuntu and its18 evidence files were retrieved.
Run: commercial61-native-087-b99f1a88-ab5f-4cf5-9329-b416e39c5a67.
Do not boot306 again. Latest retained experimental entries are173 and306.

The observer opened the actual Himax event2 with10 slots, ran its bounded
window and exited normally: result0, frames0, max_concurrent0, dropped0.
There was no user input during that window. Physical multitouch and app-level
gestures remain pending, not failed or passed. Original Bluetooth enable
completed again and its switch state became on; the fix survived integration.
See `commercial61-native-306/driver-analysis-313.json`.

Audio inventory311 and route contract312 are read-only Ubuntu observations.
The deployed UCM's HUAWEI condition explicitly includes its existing X13s
profile; speaker playback maps to `hw:${CardId},1`, headphones to0. Reuse the
actual deployed, reviewed UCM dependencies rather than inventing amplifier
routes. Neither routes nor mixer values were modified and no microphone was
recorded. The original primary audio library is the reference l410_audio_vdi
and contains `/dev/l410_audio_pcm.sock` and the capture endpoint. Next connect
a real ALSA backend with explicit failure/accepted-frame reporting; remove
fallback pacing/silence-as-success from any adapted VDI. Keep microphone
capture unimplemented rather than returning fake samples. No audible test
or120Hz change has happened yet.

Future retrieval must exclude306 as well as235,253,262,266,276,285,294,297.
Keep using the shortened360-second budget with120-second cleanup reserve,
retain essential identity/transfer/default-boot checks and omit disk suites.
