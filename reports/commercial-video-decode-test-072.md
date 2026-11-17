# Native Original Video Decode Feasibility

This is an Ubuntu-side native decode test, NOT operational HarmonyOS boot 072.
No new 072 boot candidate has been installed or run. Goal remains active.

All eight exact original StartupGuide MP4 assets decoded on the MateBook using
its existing FFmpeg 8.0.1-3ubuntu2, two decoder threads and frame-MD5 output.
No hardware-acceleration option was requested. Total: 1980 frames, matching
the eight original streams' reported frame counts. All ffmpeg exits were zero
and stderr empty; each source SHA256 was checked against the original HAP.

| Original Asset | Codec | Dimensions | Frames | Decode Seconds |
| --- | --- | --- | --- | --- |
| ball_bg_land | H.264 | 2560x1440 | 300 | 3.802 |
| ball_bg_port | H.264 | 1080x2340 | 300 | 2.652 |
| enter_home_land | HEVC | 2560x1440 | 279 | 3.603 |
| enter_home_port | HEVC | 1080x2340 | 260 | 2.357 |
| welcome_land_one | HEVC | 2560x1440 | 60 | 0.897 |
| welcome_land_two | HEVC | 2560x1440 | 360 | 4.590 |
| welcome_port_one | HEVC | 1080x2340 | 60 | 0.652 |
| welcome_port_two | HEVC | 1080x2340 | 361 | 3.211 |

These timings include frame hashing and output, not a performance guarantee
for concurrent HarmonyOS playback. All streams probe as yuv420p. Original
result, hashes and source-file sizes are in commercial-video-decode-test-072/
result.json. Native outputs remain in the private host work directory named
there. No packages installed, system configuration changed or reboot performed;
boot ID remained 5bfb4899-311c-4775-98e9-b304a7d9e023 and screen-off timer active.

## Integration Required

071 established original runtime AVC/HEVC adapters use the L410 socket bridges,
not the nominal stock image libraries inspected in 070. Original helper
launchers require an external Kylin glibc sysroot and old FFmpeg 58 dependency
tree; both original init-managed helpers exited 1. Exact failed shell test is
still unobserved. Effective library provenance and dependencies are retained
in commercial-effective-codecs-audit-071/result.json.

Next implementation should retain the original bridge wire contracts and
original service credentials, while supplying real FFmpeg software decoding.
Validate CREATE, parser consumption, output slot ownership, timestamps,
EAGAIN/backpressure, drain/reset and malformed-input handling against real
original H.264/HEVC assets before a new bounded native boot. Use decoded YUV
frames, never invented frames or success returns. Do not transplant HiSilicon
device assumptions into MateBook backend code.

Ubuntu decode success does not establish HarmonyOS helper loading, successful
original video playback, a visible welcome page, desktop or normal interaction.
All remain separate required runtime evidence.
