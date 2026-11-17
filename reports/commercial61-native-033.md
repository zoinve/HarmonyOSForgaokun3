# Commercial 033 — public GL dispatch comparison on the original swap thread

032 launched the original SceneBoard and reached its real desktop/wallpaper render-tree nodes, but both the real composer input/output and late EGL back-buffer observations remained black. No genuine desktop was verified. All operations through 032 are closed and must not be repeated.

The single hypothesis is that the original commercial GLES frontend and the own Mesa bridge might not see the same GL state on the actual RenderService swap thread. 033 observes public GL version/renderer, read/draw FBO, current program and viewport through both routes. It records context presence, not pointer equality: the original frontend context is a wrapper around the Mesa context. Function ownership comes from `dladdr`. `RTLD_NOLOAD` is used for original library handles, so unavailable frontend access is reported rather than manufacturing another frontend instance.

This changes only observations in the own EGL hardware provider. It does not alter hooks, read private dispatch-table offsets, replace original EGL/GLES frontends, consume GL errors, draw test pixels or change the actual swap/copy/flush results. Query availability is distinct from successful rendering. The existing EGL 031 trace has its own 208-line limit; the new comparison adds at most 32 lines (16 paired observations) per process. The original launcher with bounded 032 retries, bootstrap, commercial packages, mapper, service identities, authentication, sandbox, seccomp, composer 030 and runtime closure are retained. No SDK userland is substituted.

The binary audit corrected an earlier provenance mistake: older inspected frontend libraries were not the commercial image's binaries. See `commercial-gl-dispatch-audit-033.md` for the actual commercial hashes and read-only extraction provenance. Neither old private offsets nor public upstream source is treated as commercial ABI proof.

Offline fixture checks exercise the real query helper with controlled GL callbacks: all state fields, unavailable functions and errno restoration. They are not target GPU evidence. The three reference projects remain the baseline; genuine desktop acceptance comes before WiFi/touch/USB/external-video adaptation.

Runtime results are pending. Original images, Ubuntu current/default boot, old manual entry, enabled/active screen-off timer, trusted per-command SSH, memory admission, 32 MiB EFI reserve and unchanged 90-second target / 210-second outer software deadlines remain required. Software deadlines do not guarantee recovery from kernel/hardware hangs.

## Offline verification

Twenty scoped regressions passed. These include compiled query/state/errno fixtures and an exact source comparison proving that removing the new observation helper and its single invocation recovers the unchanged 031-instrumented provider source. The five assembled workflows passed syntax, candidate, trusted-address and screen-off-state checks. Historical operational collections were not rerun.

The own EGL provider is 91,592 bytes, SHA256 `d3eeae2c79d172d2175ba619f6fcf479379dcf3ba41275912164680f5b0a7d55`, with unchanged public exports and original commercial runtime closure. The bootstrap is byte-identical to 032. The final overlay is 773,238 bytes, SHA256 `e1f224174a166098b4bb8e0ed4f11a3f021a882759c46e49e4a8b1375fdcfd25`; ordered 001 → 017 → 016 → 033 extraction matches the full build's bytes and modes, including parent-directory ordering. These are offline checks, not desktop verification.

## Installation

Installation succeeded once: all 130 prior EFI files remained unchanged and both non-PID1 guards refused execution with exit 77. EFI free space was 218,787,840 bytes. Ubuntu default, the manual entry and enabled screen-off timer were retained. Installation selected no one-shot entry and requested no reboot. A separate single bounded 033 diagnostic run has now been launched; runtime evidence remains pending.

## Actual result (closed)

The single attempt ran on November 13 UTC (November 14 local), 18:24:06–18:26:58. All 59 retrieved files matched their remote hashes. Read-only evidence retrieval did not replay the original partition journal and left it unmounted. Configured target termination was observed. Original SceneBoard installation and process presence were confirmed, but the three actual exported frames are black: **no genuine desktop is verified**.

Eight paired observations on the real RenderService copy threads match between the original commercial GLES frontend and own Mesa path. Both report `OpenGL ES 3.2 Mesa 25.0.1`, `FD690`, read/draw FBO zero and viewport `0,0,2560,1600`; the respective thread's current program is consistently zero or one on both routes. Actual owners are the original `/system/lib64/libGLESv3.so` and own Mesa `/system/lib64/lab-commercial013/libGLESv2.so.2`. Both frontend wrapper and real Mesa contexts are present. The final two pairs occur at approximately 71.9 guest seconds, not just early boot. This does not support a public-state dispatch mismatch at the sampled boundary; it does not prove error-free draws. Four unique synchronized source/output observations remain black, the latest at 71.935 seconds. Raw-derived records are preserved in `dispatch-boundary-analysis.json`.

Preservation verification confirms standard Ubuntu boot `08c58a52-4fe8-4d94-9622-2f4a542a3fb5`, current/default entry, firmware, manual entry, all four original commercial image hashes, unmounted evidence partition and enabled/active screen-off timer. Of 130 earlier EFI files, 129 are unchanged; only the legitimate boot-managed random seed rotated. This numbered operational attempt is closed and must not be repeated or its evidence overwritten.
