# Original graphics 065: failed logging-index diagnostic

The original RenderService again created real EGL contexts and successfully called
`eglMakeCurrent` in the isolated software-Mesa / virtual-DRM guest. This is not a
desktop, physical-display or complete service-readiness result.

## Evidence and failure

- Run: `baremetal-sdk-original-init-qemu-065/result.json` and its raw serial log.
- Independent check: `original-graphics-boot-065-independent.json`.
- Original composer, allocator and RenderService UIDs/domains were preserved;
  all 18 observed SELinux samples were permissive, not disabled.
- Both attempted diagnostic-child index mounts failed with errno 2. The children
  exited 71 before executing HiLog. No decoded output or successful index mount
  was established. The attempted `/log/hilog/.dict_info.json` target was wrong;
  the retained scratch filesystem represents guest `/data`, not guest `/`.
- The 160-second observation ended by timeout. No Foundation critical fault or
  guest reboot was observed in that interval; this does not establish stability.
- Independent verification rehashed the 12 provider libraries, initrd, kernel,
  all three original SDK images and 378 historical native raw files.

The verifier initially rejected an interleaved console line that made Foundation
look like allocator_host. A reproduced offline test led to exact command-token
classification; original UID/domain assertions were retained. Completed earlier
verifiers and raw logs were not rewritten.

The scratch file used a historical **prefix**, but `mkstemp` still created an
exclusive, new random filename. There was no reuse or overwrite of prior data.

## Follow-up grounded in original code

`original-hilog-decoder-001` extracts the unmodified original decoder and its
mini-debug symbols without executing it or writing the SDK image. Its dictionary
loader uses `/data/log/dict`, formats the numeric UUID as `%08X`, reverses its
four byte pairs, scans matching filenames, and reads the genuine dictionary file.
That path is independent of the guessed cache-index fix. The corresponding
original RS dictionary exists in the recovered 064 scratch copy at
`/log/dict/2C/EB723E313C80C3605ECD369C0B8CB6` (guest `/data/log/dict/...`).

Trial 066 therefore leaves dictionaries and all providers unchanged, observes
the actual runtime file, and requests a bounded screen dump from the original
`hidumper` / RenderService. Its result is pending, not assumed successful.

All work here is local, isolated QEMU work. No MateBook host connection, host boot
change, credential modification, fabricated readiness or original service patch
was performed.
