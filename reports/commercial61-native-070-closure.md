# Native 070 Closure

Run commercial61-native-070-801065ed-761c-4c40-9fad-e375fdcb04c5 completed
once and returned Ubuntu. Do not rerun. Desktop goal remains active.

## Proven Resource Progress

46 exact original rawfiles were supplied adjacent to original preinstall HAP
through the RAM-only read-only system overlay. Original HAP and installed
records remained unchanged. Original StartupGuide rawfile errors changed:

- FindRawFile realpath errors: 16 in 069, zero in 070.
- Video filename errors: four in 069, zero in 070.
- Video media source setting failures: three in 069, zero in 070.

070 observed two StartupGuide PIDs, so counts are not rate-normalized, but both
had no matching source resolution failure. Root file visibility alone is not
the success criterion: original app logs prove it progressed past that stage.
Original SystemResources AddResource failure remains once in both runs.

## Next Actual Failure

Original media pipeline now reaches codec creation/configuration. At guest
57.911s CodecServer records forwarded caller PID 5762 and original media_service
caller PID 1216. HEVC creation succeeds at the server abstraction but the
underlying decoder Start reports 'hevc deocder create failed'. AVC FCodec then
reports 'Start codec failed: cannot open avcodec'. Original app receives
331350556 video-decode errors. This is distinct from missing rawfiles.

Offline original image inspection finds libl410ffmpeg.z.so containing the
helper endpoint /data/local/tmp/l410-kylin-h264x-decoder.sock and identifying
itself as an L410 Kylin hardware H.264 bridge. Do not assume HEVC shares this
cause: libhevcdec_ohos.z.so is a different implementation requiring audit.

## Pixels And Return

Full capture at guest 120.025423s is byte-identical to 068/069 PPMs: 4652
nonblack pixels, zero clockwise source/scanout pixel differences. No complete
desktop or interaction verified. Normal bounded target timeout and observer
stop are recorded; all 67 retrieved files matched remote hashes.

Return verification: Ubuntu current/default, original four images and firmware
unchanged, screen-off timer enabled/active and lab partition unmounted.
Subsequent boot retention archived and removed 068 entry, preserving only
069/070 experimental entries, original manual entry and Ubuntu default. See
boot-entry-retention-20261114T205819202382Z/result.json. Shared payloads retained.

## Reference Relevance

L410 video-h264/fcodec_h264_bridge.c forwards original FFmpeg operations except
its real H.264 bridge path; video-hevc/hevcdec_kylin_proxy.c sends compressed
input via shared memfds/SEQPACKET to a helper and returns actual YUV output.
Its supplied helper depends on Kylin FFmpeg and original hardware OMX decoders.
These are real codec bridges, not ready-made MateBook hardware drivers.
HarmonyMac inspected Mesa build scripts disable video codecs; Linux
Compatibility Platform AnCo codecs encode IPC, not video decoding. No supplied
reference decoder bridge has been deployed by 070.
