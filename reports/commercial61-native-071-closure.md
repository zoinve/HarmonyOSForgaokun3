# Native 071 Closure

Run commercial61-native-071-f14cb394-c422-4bb3-9b06-109047a1be72 completed
once, normal target timeout recorded, original monitor stopped, Ubuntu returned.
Do not rerun. Full desktop and interaction remain unverified; goal is active.

## Effective Codec Discovery

Complete proc maps for original UID 1013 av_codec_service were obtained with
EOF and no stream error. Runtime shows libl410ffmpeg.z.so loaded. Inode mapping
using original image debugfs ncheck establishes the effective files:

- inode 271005: /system/lib64/l410-h264-decoder-v1/libfcodec.z.so
- inode 265869: /system/lib64/l410-codec-sandbox-v1/libhevc_decoder.z.so
- inode 265870: /system/lib64/l410-codec-sandbox-v1/libhevcdec_ohos.z.so

The 070 audit inspected different original files at their nominal paths.
Those findings remain valid for those files, not for the effective runtime
objects. 071 instruction validation refused with ENOEXEC before attaching any
codec breakpoints: zero attachments and zero codec return-register samples.
Do NOT infer nonexecution or report observed return codes from this run.
The refusal correctly prevented sampling offsets for a different ELF.

Original init logs show both l410_kylin_h264_decoder and
l410_kylin_video_decoder started then repeatedly exited with status 1. This is
not merely a service that was never started. Original launch scripts require:

- /data/local/tmp/kylin-sysroot-ro/lib/aarch64-linux-gnu/ld-2.31.so
- original executable helper and libavcodec.so.58 payload
- Kylin sysroot library search paths

The exact failed shell test was not logged; loader existence was not measured.
Do not treat external sysroot absence alone as the fully proven error cause.
Native diagnostic data is ephemeral and original userdata is not attached.
The bundled codec directory contains libavcodec.so.58 and HiSilicon OMX decoder.
MateBook software/hardware backend adaptation remains necessary to evaluate.

Reference helper uses real decoded frames and has a real per-stream Main10
software fallback. Its default hardware OMX path is Kylin-specific. Preserve
original service identity and protocol; do not fake decode success or patch
license/identity checks. Next work should repair actual backend availability,
not spend another boot targeting the wrong nominal libraries.

## Presentation And Preservation

All 67 retrieved files matched remote hashes. Full frame at 120.014561 seconds
remains byte-identical to 068/069/070 PPMs, 4652 nonblack pixels, zero clockwise
source/output pixel differences. First flush 93.392 seconds, 56 later frames.
Original graphics hardware observations: 204 attachments, no attachment errors,
lost/malformed records or instruction pointer mismatches.

Return verification passed: Ubuntu current/default, firmware and four original
images unchanged, lab partition unmounted, screen-off timer enabled/active.
Authorized cleanup archived 069 and retained experimental 070/071 plus original
manual and Ubuntu entries; shared payloads retained. Evidence:
boot-entry-retention-20261114T211210807249Z/result.json.

Image-view tool rejected image inputs; numerical image analysis is not claimed
as human visual verification. No input injection, provisioning bypass or
StartupGuide force-stop occurred.
