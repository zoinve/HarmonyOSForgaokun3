# Cross-process offscreen DMA-BUF/fence — IPC002

## Verified result

The OHOS-built probe passed on the MateBook's Ubuntu kernel, using FD690 and
Mesa 25.0.1. Producer PID 3493 and a separately executed consumer PID 3494
communicated over a private Unix socket. Before the producer waited on its
own fence or read pixels, it sent a DMA-BUF FD and native sync_file FD, then
closed the two transfer duplicates.

The consumer waited on the received fence, opened the render node independently,
imported the DMA-BUF, closed the received DMA-BUF FD after import, and read exact
opaque red/blue pixels. The producer also passed the existing EGL fence reimport,
GPU pixel and second independent GBM mapping checks. No `glFinish` was introduced.
This does not establish that the fence was initially unsignaled.

## Independent verification

`baremetal-freedreno-ipc-run-002/independent-verification.json` verifies all nine
archive and remote ELF hashes and sizes, distinct producer/consumer PIDs, exact
pixels, FD ownership markers and the live pre-start sandbox policy. Only
`renderD128` was permitted; card0 admission was denied. There were no new kernel
log lines and no FD identity warning.

Ubuntu boot ID/default, absent one-shot/stale diagnostic entries and automatic
screen-off state were unchanged. The screen verifier refused setters; it did not
turn the screen off to conceal a failure. No physical screen observation is claimed.

Archive: 6,406,772 bytes, SHA-256
`9474ca56a5f828c29399f7d8c9319ca2bb3f2fca01efb4d076e4b468694257eb`.

## Test history and limits

CPU-only tests exercised genuine cross-process SCM_RIGHTS ownership/CLOEXEC and
malformed packet/count/stride/modifier/ancillary-truncation rejection without FD
leaks. Package001 failed strict compilation in an SDK CMSG_NXTHDR macro. The
private protocol now uses bounded ancillary iteration, retaining `-Werror` and
leaving SDK headers untouched; fresh package002 compiled successfully.

This is a private, single-plane linear ARGB8888, 16×16 transport test, not the
HarmonyOS HDI serialization protocol or a complete compositor. The new
cross-process path has not yet run on the custom native kernel. Candidate014
preparation retains the proven candidate011 kernel/init/launcher/libraries and
requires that only the private probe record change. No KMS, modeset, identity,
policy, SDK image or Ubuntu library changes were made.
