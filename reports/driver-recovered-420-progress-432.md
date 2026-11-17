# Recovered420 Driver Evidence

Date:2026-11-17, Asia/Shanghai. Full basic-driver objective remains incomplete.
Priority remains Bluetooth, physical multitouch, audio, then actual120Hz.

## Recovery And Preservation

After the user reported recovery,422 authenticated the current Ubuntu boot
433494a1-e65c-4b1e-a8e4-37cca468afe8, kernel7.1.0-rc3-gaokun3+,
at2026-11-17T01:11:32.409208Z (09:11:32 Asia/Shanghai).
424 verified Ubuntu current/default, no oneshot, enabled/active screen-off,
the expected lab partition identity and its unmounted state. No filesystem,
disk-hash or tree-validation suite ran. No new boot or installation was requested.

422 retrieved16 files under WSL, readonly/noload, with transfer integrity verified.
Run:commercial61-native-087-ab81182b-7f50-46d5-ba48-2708cd79ce53.
The final cumulative log is phase-180.log. No original.tar was persisted.
The earlier426 timeout and430 failed connection observations remain unchanged;
they accurately describe those earlier times, not the now-recovered state.
Current boot identity does not establish the earlier reboot or SSH failure cause.

## Audio420

425 analysis confirms the original renderer/services/VDI opened real speaker
PCM1 three times. ALSA accepted348480/191040/202560 frames, with0/10402/11053
nonzero frames. Total742080 accepted,21455 nonzero; operation errors0.
The public renderer completed22 callbacks,19148 source nonzero frames,
zero invalid buffers and zero API failures. Pause/resume position advanced
37392 to80592; both snapshots had zero underflows. These are pipeline results,
not independent acoustic confirmation.

The shared card had three acquire/release pairs, all releases result0. The
new broker listened with two workers, then shut down with active_workers0 and
status0. Its supervisor recorded forced0/raw_wait_status0. There were no capture
ready, I/O or end records; real microphone capture and duplex remain untested.
No ambient capture probe was introduced. The working413 dead-query-socket fix
still is NOT part of frozen420 and needs a new candidate before target testing.

Original audio_server UID1041 retained six adapter mappings, real event10 fd16
and an OS_InputEvent thread, observed twice. Initial jack snapshot0 agrees with
the readonly hardware observations. Replayed startup trace dumps are not two
physical plug events. Physical hotplug, headphones and acoustics remain pending.

## Bluetooth And Touch

431 shows Bluetooth enable completed and switch on. Three extended scan enables
and two disables (opcode2042) all received controller status0. The advertising
observer logged a lower bound of one LE report packet. It logs the first and
every64th packet; do not call this an exact device count or diagnose a scan
failure from the small lower bound. No Classic discovery request was observed.
Pairing, reconnection, low-power behavior and Settings nearby-list acceptance
remain unverified. No root-aa retry, borrowed token or permission bypass ran.

The passive touch observer ended normally with frames0/max_concurrent0/dropped0.
No physical interaction was captured; multi-contact and app gestures have not
passed.120Hz remains unchanged and unverified.

## Exit Evidence And Storage

The diagnostic intentionally recorded target_timeout1 and target exit status9;
this is not proof of a spontaneous service crash. Persistent cleanup recorded
20 data mounts removed, remaining0, inner syncfs/backing fsync/outer syncfs1,
and finish status0. The final persisted phase ends after NATIVE_DIAGNOSTIC_END;
it does not contain the later global cleanup/reboot outcome. Do not infer a
specific reboot/connection root cause or blame microphone capture from this.

427 losslessly compressed11 completed logs, saving113438804 bytes, with
decompressed integrity verified. Use226 open_log for subsequent reads.
428 removed only retired, unreferenced set401.img (3247001 bytes); all active
boot references remain present and ESP free space is38359040 bytes. Entries
173/420, protected desktop/data165/197, original images and canonical local
builds remain retained. USB181 work remains paused and untouched.

For future retrieval, exclude all prior experiments through420, including
235/253/262/266/276/285/294/297/306/321/331/341/353/365/378/385/394/401/420.
Do not boot420 again to replace existing evidence. New code needs a new number.
