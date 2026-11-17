# Native 071: Original Codec Return Registers

Retains exact 070 resources, original services, EGL/composer and full-frame
capture. Only existing archive init/bootstrap differ. Adds read-only proc
maps/status inventory for original UID 1013 av_codec_service, plus a separate
execution-breakpoint observer in the existing bounded native monitor.

Four verified original ELF locations capture x0..x6 registers:

- libfcodec.z.so VA 0x15d5c: result immediately after avcodec_open2.
- libhevc_decoder.z.so VA 0x16750: result after decoder-create callback.
- libhevcdec_ohos.z.so VA 0x498e4: IHW265D_CheckParams return.
- libhevcdec_ohos.z.so VA 0x49920: HW265D_MallocHandle return.

Executable PT_LOAD mappings establish file offsets. Runtime checks compare
original instruction bytes and executable mapping device/inode. No private
objects, process memory or compressed input are read. No instruction is
replaced. Public proc status verifies original four UID fields; PID namespace
must match the isolated target. Unmapped codecs are skipped and rechecked at
later existing ticks, not represented as failed execution. Late attachment
can miss initial calls; absence remains inconclusive.

Admission: exact generated source delta, ASan/UBSan host helper tests, native
cross-compilation, exact archive delta and ordered overlay equality passed.
Strict host test initially rejected fixture indentation; the corrected r2
fixture passed without changing compiled native observer behavior.

Runtime success remains unproven. Return registers identify the next actual
failure; a green observer test cannot establish functioning desktop or video.
