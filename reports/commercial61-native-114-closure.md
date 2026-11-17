# OOBE comparison 114: guide stopped, original SceneBoard froze and restarted

Exactly one completed bounded boot. Do not rerun 114 or overwrite its evidence.
Start: 2026-11-15T17:42:33.468911+00:00.
Ubuntu return: 2026-11-15T17:46:40.445384+00:00.
Run: commercial61-native-087-34528a49-dbee-4569-86d7-5379123af688.
Ubuntu boot ID: a9a9a1ff-eb91-490e-b439-5746658b2204.
Final phase-121.log records target_timeout=1 and target PID 441 exit status 9.

## Change and observed outcome

The only changed archive member was the development reference startup script.
Its second SceneBoard start request was replaced by an existing-process guard.
The original early account/Home bridge, runtime at its verified 108 path,
kernel, original services, identities, setup state and recovery were unchanged.
Six script tests and three isolation guards passed before installation; full
ordered-overlay reconstruction matched the complete archive. Four additional
command-parser unit tests passed.

The runtime log contains OOBE114_EXISTING_SCENEBOARD_NO_SECOND_START. The
single reference aa force-stop succeeded. Original appspawn independently
records guide PID 6906 exiting with code 0 at 2026-11-16 01:44:10.059 local
time. Immediately following the script, WMS metadata lists SCBDesktop4 owned
by SceneBoard PID 5000 as window 7, with focus window 7. This is metadata,
not proof of rendered interactive desktop pixels.

Original HiLog and a complete decoded original fault snapshot establish:

- 01:44:01.094: PID 5000 starts the synchronous trusted-device-list query.
- 01:44:08.018: original AppDfr reports THREAD_BLOCK_3S for PID 5000.
- 01:44:10.059: original guide PID 6906 exits after the reference stop.
- 01:44:13.018: original AppDfr reports THREAD_BLOCK_6S for PID 5000.
- 01:44:16.519: original AppMS kills PID 5000 for THREAD_BLOCK_6S.
- 01:44:16.579: appspawn observes SceneBoard PID 5000 exit with signal 9.
- 01:44:16.607: appspawn creates replacement SceneBoard PID 9079.
- 01:44:17.611: PID 9079 normally starts OOBE during its initialization.
- 01:44:18.838: appspawn creates guide PID 9876.

All these timestamps are 2026-11-16 Asia/Shanghai. The freeze reports precede
the guide stop. Complete original fault data shows PID 5000's main thread in
condition_variable/future wait through libcollabfwk_devicedetect_client,
libcfwk_devicepicker_client and Js_GetTrustedDeviceListSync.

At uptime 90, 110, 130 and 145, PID 9079 owns SceneBoard and guide PID 9876
owns focus window 8. Removing the second startup owner was not sufficient.
The exact old callback message "start oobe again" is absent, but that does
not mean OOBE stayed dismissed: here a replacement SceneBoard starts it anew.

## Evidence and limitations

130 retrieved files match remote hashes; read-only noload retrieval finished
and the partition is unmounted. HiLog SHA256:
a456b2cdaf467151a97444822f6987fc5b4adfdc95dc102bb2d88d09e808711b.
See reference-runtime-analysis.json, oobe-single-launch-analysis.json and
oobe-scene-restart-analysis.json under reports/commercial61-native-114.
The last report supplements the first analyzer's exact-message-only recovery
flag and records the independently proven process restart chain.

Original aa logs emit only argv[0] and argv[1], explicitly ignoring later
arguments. Therefore empty bundle-matching arrays in the initial command
analysis are not evidence of no invocation. Two executable invocations are
observed: early /usr/bin/aa start and later /system/bin/aa force-stop; bundle
association additionally uses the script and lifecycle records.

Both expected full-frame exports full-ready-068 and full-ready-075 are absent
from this run. Their offline readers failed on missing source files; no
successful pixel or interaction analysis is claimed and the boot was not
replayed to obtain them. Desktop, interaction and activation remain unverified.
The credential audit passed all 130 files / 361465606 bytes; no WPA PSK exported.

## Preservation and next action

Ubuntu remains current/default; firmware and all four original image hashes
are unchanged. Screen-off timer remains enabled/active. The manual entry is
retained. 162 prior EFI files are unchanged, apart from the boot-managed random
seed and the hash-archived authorized removal of entry 108. Current experiment
entry files are 109 and 114; shared payloads remain. Retention archive:
boot-entry-retention-20261115T174217722577Z.

Stay on the OOBE-to-desktop path. Investigate the original synchronous query's
reference-runtime differences and actual server wait, not repeated guide kills,
watchdog removal, fabricated activation, or broad kernel migration. No kernel
adaptation was performed. The stable interactive native desktop goal is active
and not achieved.
