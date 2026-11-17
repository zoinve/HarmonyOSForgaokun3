# Original Decoder Input Audit

Read-only original system image extraction. No libraries executed, patched or
injected. Results and complete original ELF disassemblies are retained under
commercial-decoder-audit-070/.

- libhevcdec_ohos.z.so: 584232 bytes, SHA256
  63afbe44aa6826abec38396f2ed18db101ebb9704443387ce1e9795e21e3fef7.
  Depends only on libc.so. Export HEVC_CreateDecoder at 0x806b4 is a CFI jump
  trampoline to 0x4afb8, NOT an empty decoder stub. That function calls the
  implemented IHW265D_Create via 0x80684 -> 0x498b0 and converts its nonzero
  result to -1. A short export trampoline does not imply fake implementation.
- libhevc_decoder.z.so: original service adapter, 254712 bytes. Its Start
  method is exported at 0x1657c. Runtime reports underlying creation failure.
- libfcodec.z.so: 259464 bytes, SHA256
  0bc475ded266f428b0c40633f85dd1347de2aa208876b142c414b0499f5c9527.
  DT_NEEDED includes libohosffmpeg.z.so, NOT libl410ffmpeg.z.so. Runtime says
  avcodec cannot open; the actual return code remains unobserved.
- libl410ffmpeg.z.so: 22512 bytes, SHA256
  15173ddd8c34613f4e5a729c8481b7c741108b71396a47f2d3fdd9b1b5243145.
  Real H.264 bridge with socket string
  /data/local/tmp/l410-kylin-h264x-decoder.sock. Its presence on disk does NOT
  prove that av_codec_service loaded or called it. Do not launch a helper
  assuming that alone fixes stock FCodec.
- chipset-sdk/libohosffmpeg.z.so: 5835560 bytes, SHA256
  553d5f658994f5890827abc25ded7d260b8f0396bc22d001cab6c0afe424f999.
  Depends only on libc.so and exports original avcodec operations.

The L410 H.264 bridge loads stock FFmpeg and forwards other codec operations;
its HEVC bridge uses actual shared-memory compressed-input/YUV-output helper
communication. Supplied helper selects Kylin h264_omx_dec/hevc_omx_dec and is
not a MateBook driver. No reference bridge deployed in 070.

Next evidence needed: actual original av_codec_service loaded-object paths,
actual failed original codec return values and the corresponding creation
failure branch. Keep observations at public API/ELF/register boundaries and
retain real input/output validation; no private live-object inspection,
instruction patching or fabricated codec success.
