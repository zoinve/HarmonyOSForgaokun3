# Commercial 030 — fresh source/output frame evidence

029 established real EGL initialization, current contexts and successful original RenderService presentation calls, plus original SceneBoard nodes reaching RenderService. It did not establish desktop pixels. Its capture implementation updated the PPM only for the first five and every thirtieth commit; three later exported black files could not independently establish frame freshness.

030 changes diagnostic observation only. The own composer captures its first five completed scanouts, then at most once per second (128 maximum). Each capture samples actual client and completed output RGB values under DMA-BUF read synchronization, records validity/nonblack counts/checksums, framebuffer, sequence and monotonic time in the existing authorized performance trace. No synthetic frame is rendered, no original return decisions change and alpha alone is not treated as nonblack content. Failed sampling is recorded as unavailable, never as success.

The observer additionally records before/after file size and modification time alongside each exported PPM. This allows inconsistent or stale files to be distinguished from current display evidence. The original 029 own EGL provider, commercial frontend, packages, mapper, authentication, sandbox, seccomp and service identities remain unchanged. All three adaptation references remain the baseline, not their insecure test identities or completion shortcuts.

The first offline native build exposed a missing `time.h` declaration. Its source and compiler logs remain in the untouched `commercial61-native-030` WSL directory. The corrected successful build uses the independent `commercial61-native-030-r2` directory; deployment/run identifiers remain 030. Nothing was installed by the failed compilation.

Runtime results are pending. Original-image hash checks, standard Ubuntu default/current guards, enabled/active screen-off timer, strict trusted SSH, 32 MiB EFI reserve, memory admission and the existing bounded diagnostic return remain required. Neither successful offline compilation nor pixel statistics alone establish a usable original desktop. WiFi, touch, USB and external-video adaptation follow genuine desktop acceptance as requested.

## Offline evidence

Fourteen scoped regressions passed, including compiled real RGB sampling with alpha/stride/bounds cases, unchanged original composer render/commit bodies, prior EGL return/errno fixtures and actual timeout/memory-admission tests. The historical operational collection was not rerun. The own composer is 84,696 bytes, SHA256 `68ebc2e3d6ce9e6f05a4eb735c02253d5641d9c2319afe38e66f311518fb518d`; its public exports and original-commercial runtime closure are unchanged.

The final overlay is 770,836 bytes, SHA256 `b9b3bb489dbe198a104d6488a134e8040e86121f9bdb7d905d72a6a297fe9376`. Ordered 001 → 017 → 016 → 030 extraction verifies all parent directories and final bytes/modes against the complete build. Previous hardware archives remain unchanged. Installation is pending; there is no 030 guest or desktop result yet.

## Installation

Installation succeeded once: all 124 prior EFI files were unchanged, both non-PID1 execution guards refused with exit 77, and EFI free space was 221,134,848 bytes. Ubuntu default, enabled screen-off timer and the old manual entry were preserved. Installation did not select a one-shot entry or reboot. A separately guarded single 030 diagnostic attempt has been launched; actual frame results remain pending.

## Actual result (closed)

The single attempt ran on 2026-11-13, 17:42:07–17:44:59 UTC (local November 14). All 59 retrieved files matched their remote hashes. Retrieval used read-only `noload` access without journal replay and unmounted the evidence partition. Configured target termination is recorded. Original SceneBoard remains observable, but all three actual 160×256 PPM exports are black: **no genuine desktop has been verified**.

The new observations narrow the boundary. Four completed scanouts at guest times 12.12, 14.45, 14.49 and **75.54 seconds** have valid, synchronized client-buffer and output-buffer samples. All 40,960 RGB samples in each are black on both sides; the client is 2560×1600, stride 10240, format 12, and the output is GPU-backed. Source mapping/status checks succeeded. The final PPM export at guest 80.41 seconds has a stable before/after size and modification time corresponding to the 75.54-second update. Thus the final black export is not merely the original early-boot PPM left untouched. Detailed raw-derived records are in `frame-evidence-analysis.json`.

This shifts investigation upstream of the compositor's sampled input, not to another speculative EGL-initialization or security change. It does not yet distinguish black RenderService content from a problem in the own EGL copy into that input. Original SceneBoard desktop/wallpaper nodes are registered on the original RenderService tree; registration alone is not rendered desktop acceptance.

Post-return verification confirms standard Ubuntu boot ID `120d2e4d-0019-46fe-8ea6-e72c193c2572`, current/default entry, firmware, manual entry, all four original-commercial image hashes, unmounted LAB partition and enabled/active screen-off timer. Of 124 prior EFI files, 123 are unchanged; only the legitimate boot-managed random seed rotated. This numbered operational attempt and its logs are closed and must not be rerun or overwritten.
