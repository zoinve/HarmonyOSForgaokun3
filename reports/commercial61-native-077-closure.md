# Native 077: guide stop works, SceneBoard restart relaunches guide

## Verified changes and return

- One run: commercial61-native-077-c1f4906d-8339-42bd-8258-4d6d74c7b73c,
  2026-11-15 02:43:15 to 02:46:57 UTC. All 73 recovered file hashes matched.
- Init accepts the short script argv. AccessToken log line 26542 records
  matebook_desktop077 with permSize 5. No supplied token or original service
  identity change.
- snapshot075-commercial-direct-desktop075.log explicitly reports both
  `start ability successfully.` and `force stop process successfully.`
- At 67.98 seconds guide pidof returns 1 (absent), SceneBoard pidof returns 0.
  WMS reports SCBDesktop window 7 focused, but still lists the old guide window.
  Neither WMS registration nor this short absence establishes a usable desktop.
- The boot reaches its bounded target_timeout and TARGET_EXIT records. Returned
  Ubuntu boot ID 0451dd98-6589-4eb0-a8a0-b4e9fac5fc32. Preservation verifier
  passes Ubuntu current/default, firmware, original images, screen-off timer,
  manual entry and unmounted LAB. Retained experimental entry files are 076/077.

## Why OOBE remains visible

Authoritative interactive-hilog030.log sequence:

- 236043: 63.272 s, SceneBoard PID 4248 THREAD_BLOCK_3S (before guide stop).
- 250187: 64.917 s, original AMS Kill process request for the guide.
- 255116: 68.232 s, SceneBoard PID 4248 THREAD_BLOCK_6S, forceExit 1.
- 259308: 71.535 s, appspawn starts SceneBoard again (later PID 7841).
- 274218: 73.898 s, appspawn starts the guide again; PID 8908 logs welcome
  at 79.387 s (286765).
- 356264: 91.870 s, SceneBoard PID 7841 THREAD_BLOCK_6S, forceExit 1.
- 375552: 95.154 s, another SceneBoard start (later PID 10732).
- 388423: 97.413 s, another guide start; PID 11744 logs welcome at 102.906 s
  (398773).

The stop is real but transient. Do not classify it as persistent dismissal or
activation. Freeze starts before the stop, so stopping the guide is not proven
to cause the first SceneBoard freeze. Next work should inspect the original
public freeze diagnostics and blocking dependencies, not disable watchdogs,
change provisioning records, or repeatedly kill the guide without attribution.

## Pixels and input limits

- Both 2560x1600 source / 1600x2560 output exports validate with zero rotation
  pixel differences. Source captures differ in 8564 pixels. Local OCR reads
  `0` before input and `欢迎 0` afterward; this is not desktop proof.
- Before-source PPM SHA256:
  22553f7e8834b9bf426164e206eba6e201cfac3a99bf63c18867ff8d2cc465f7.
- Own inherited bootstrap still logs COMMERCIAL075_KEYBOARD, not COMMERCIAL077,
  because it is unchanged. phase-062.log:272870 records event6 LEFTMETA writes
  48/48 bytes. The generic 077 input analyzer therefore misses that writer
  marker; preserve its initial output and do not treat the missing match as
  absence of the write. Any corrected analysis needs a new evidence filename.
- SceneBoard logs PreLogoKeyEvent down/up at 132.985 / 133.051 seconds, but no
  verified desktop response follows. Interaction remains unverified.
- Public prefix contains 109 frame records and 77496 codec SendFrame failures.
  Prefix logs are not EOF or proof of successful decoding.

Desktop, persistent guide dismissal, interaction and activation remain false.
