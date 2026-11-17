# Driver Progress After331

Date:2026-11-17, Asia/Shanghai. Preserve user order: Bluetooth, multitouch,
audio,120Hz. Overall goal remains active, not complete.

## Completed Work This Turn

Retrieved321 once. Run:commercial61-native-087-95203bb3-3336-49f3-acbe-41e295adf1e2.
Original audio_server created48kHz stereo S32_LE output; original audio_host
used the adapted VDI and real UCM/ALSA speaker PCM. Actual submitted frames:
347520. Playback position advanced. Acoustic output and nonzero samples are
not verified. See audio-result-327.md and321/audio-analysis-336.json.

Fixed a code-inspected idle transport bug in native-audio-server-316.c:
wait for a complete request to begin before applying the receive timeout.
Partial headers/payloads remain timeout bounded. Shutdown remains poll bounded.
This did not establish the cause of321 stream termination. Test330 passed:
official-header shared library build, ARM64 server build, sanitized existing
contract tests and new329 idle-over3seconds/partial-header/EOF/stop tests.
No hardware acceptance is inferred from test doubles.

331 was built, installed and booted exactly once. It returned to Ubuntu at
2026-11-16T18:54:57.699008Z (2026-11-17 02:54:57 Asia/Shanghai).
Run:commercial61-native-087-42a41779-0cdb-4be0-b566-44ceab72220a.
Collector333 retrieved18 files. Do not boot331 again.

331 original services again opened real speaker PCM, submitted350400 frames
(7.3seconds at48kHz), and observed advancing playback position. Its first64
logged transactions have no I/O errors and consistent submitted/played/delay
accounting. Later transactions are not exhaustively logged. Stream-end result0;
no AUDIO329_TRANSPORT diagnostic. This verifies integration after the change,
not a hardware idle/restart scenario. Broker shutdown was bounded by the runtime.
See commercial61-native-331/audio-analysis-336.json.

## Remaining Acceptance

Bluetooth enablement and switch-on succeeded in both321 and331. Pairing,
discovery, reconnection and low-power behavior remain unverified.

Both physical touch monitors completed normally with0 frames and0 concurrent
contacts. No user touched the screen during observation. Do not label physical
multitouch or app gestures as passed. Retain existing MMI and read-only observer.

Audio acoustic playback, nonzero sample content, idle/restart on target,
headphone routing, microphone and user volume/mute remain pending. Microphone
currently returns unsupported, never fake silence. A genuine system media
renderer already exercised the output, so another direct-ALSA probe would not
provide stronger original-service evidence. Do not record ambient audio to
claim playback. Keep120Hz unchanged until the audio work is further verified.

## Preservation And Storage

ESP free-space guard rejected the first331 install before any write. Cleanup334
removed only retired, unreferenced set297.img/set306.img:2263896 bytes.
331 then installed successfully. Latest experiment entries are173 and331;
321 entry was archived before retirement. No shared boot dependency was deleted.
Desktop173, active165, current197, original images, Ubuntu default boot and
enabled/active screen-off timer were preserved by essential guards.
No disk hash/fsck/tree-comparison suite was rerun.

Compression335 saved102214871 bytes from10 completed321 logs, with the existing
lossless compression integrity checks. Read historical logs using open_log
from compress-historical-logs-226.py. Do not recreate raw duplicate logs.
Compression338 subsequently saved103252321 bytes from10 completed331 logs.
331 touch observer and audio broker both exited normally, forced=0/status=0.

Future retrieval exclusions must include235,253,262,266,276,285,294,297,306,321,331.
Use a new numbered experiment for new code. Preserve360-second window and
120-second cleanup reserve; never retry an old boot merely because SSH times out.
