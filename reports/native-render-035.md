# 035 split-stage diagnosis — completed bounded run

035 preserves the 034 pixel algorithm and 032 cursor adapter, adding only timing boundaries. Nine boot artifacts and 72 ASan/UBSan pixel/crop/scaling/color combinations passed. Both native non-PID1 guards refused execution. The tiny overlay changes only outer `init` and the instrumented composer; 100 preexisting EFI files remained unchanged. The original images, Ubuntu default and manual 031/032 entries remain intact.

The single operational attempt returned automatically to Ubuntu boot ID `9a861837-a46a-461a-9de0-de2a4f487108`. No one-shot remains, automatic screen-off is active. Read-only `ro,noload` retrieval recovered 71 files with matching remote/local hashes from `native-interactive-035-3fd91bcc-ebaa-4548-a7c1-e9418e7d4080`, then unmounted the original partition. No journal replay or repeated operational trial occurred.

Deduplicated, capped timing records show:

| Stage | Samples | Mean |
| --- | ---: | ---: |
| DMA client → cached RAM | 22 | 14.933 ms |
| NEON rotation | 21 | 5.303 ms |
| Owned background → scanout, including cursor | 21 | 1.934 ms |
| Complete copy/rotation | 21 | 22.849 ms |

Sampling is capped globally per process and the final partial sample explains unequal counts. Timings include diagnostic overhead. The dominant cost is reading the DMA client into CPU-cached memory, not simply rotating cached pixels. This supports probing a direct DMA-import GPU pipeline rather than continuing isolated NEON tuning. FD690 remains active. No desktop FPS or physical cursor/click acceptance is inferred.

The first offscreen GPU probe (036, no KMS modeset) failed before drawing because the GBM EGL display offered no matching pbuffer configuration. Its exit status and stderr are retained. Candidate probe 037 requests a config without a window-surface requirement, retaining the same real hardware and full pixel comparison. Do not treat a failed probe as renderer success or deploy an unverified pipeline.
