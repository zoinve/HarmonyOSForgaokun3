# Audio321 Result

Date:2026-11-17, Asia/Shanghai.
Run:commercial61-native-087-95203bb3-3336-49f3-acbe-41e295adf1e2.
Returned to Ubuntu automatically; collector324 retrieved18 files.
Do not repeat321. Add321 to future retrieval exclusions.

Original audio_server created its primary48kHz stereo S32_LE render, original
audio_host loaded the RAM-bound VDI. phase-181.log line32552 records actual
UCM speaker PCM initialization, period960 and buffer3840. Actual ALSA writes
accepted3840 bytes each and observed playback position advancing. Line76721
records347520 submitted frames (7.24seconds at48kHz). This is original-service
to real PCM integration, not acoustic acceptance. Only the first64 transactions
are logged; no complete later error count or nonzero-sample claim is inferred.

Original Bluetooth enablement completed again (hilog117136), and switch-on
was recorded (118283). Discovery, pairing and reconnection remain pending.
Touch monitor completed normally: result0, frames0, max_concurrent0, dropped0.
No physical contacts occurred; neither multitouch nor app gestures pass yet.

Audio329 fixes a code-inspected lifecycle risk: the previous3-second receive
timeout disconnected an idle renderer. Poll for readiness, retaining socket
timeouts for partial requests and payloads. This does not prove why321 ended.
Transport termination now gets a distinct diagnostic. This change is not in321
and needs a new candidate for target testing.

Microphone, headphones, audible output and120Hz remain unaccepted.
Desktop173/data165 and original images remain untouched; Ubuntu stays default.
No disk hash/fsck/tree validation suite was run.
