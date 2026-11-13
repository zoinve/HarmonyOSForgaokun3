# 041: original-service FD690 GPU composition candidate

## Why the pipeline changed

035 split timings isolated approximately 14.9 ms in CPU reads of the client DMA buffer. NEON improved rotation but cannot remove that readback. The new path imports the real client DMA buffer, rotates/crops/scales into an owned GPU background, then draws that background and the real MMI cursor into a back scanout buffer. No software-renderer success is accepted.

The 040 capability probe established that GBM-owned linear buffers can be imported by the tested Mesa path while the earlier DUMB probes failed. It did not establish the exact internal cause of those failures. 041 therefore allocates its GPU scanouts through GBM and imports their handles into the original KMS device; it does not guess a stride or alter the kernel.

## Lifetime and service contract

- The original HDI composer API, service UID/groups, input-fence waits and KMS page-flip ownership remain intact. Only back buffers are rendered. Imported KMS handles use GEM_CLOSE, not DESTROY_DUMB.
- A private EGL context is bound and unbound under the existing composer mutex. Both normal commit and the idle cursor worker may use it serially.
- The clean background is owned by the GPU path. Idle cursor repaint never reads a prior, possibly released client FD. Cursor coordinates/visibility still come from the original MMI adapter; no input is injected or RS surface fabricated.
- Initial completion uses real `glFinish`; returning a synchronous fence of -1 does not pretend that asynchronous work has finished. Native-fence optimization is not claimed here.
- Failed GPU initialization retains DUMB/NEON composition. Failed frame import invalidates GPU background and takes the existing CPU path. Fallback is logged, not counted as GPU success.

## Verification before original-service execution

The actual helper passed a bounded FD690 offscreen test under Ubuntu: full RGB comparison at small and full panel sizes, four corner cursors, hide/restore, input-buffer release followed by idle repaint, and context migration to another thread. This was a root diagnostic using Ubuntu Mesa, not proof of original service credentials or HarmonyOS Mesa behavior.

The independently compiled OHOS composer linked without undefined symbols or compiler diagnostics. Original 034 artifacts and both cursor adapters are unchanged. Nine boot-artifact hashes, two real non-PID1 refusal guards, and a complete initramfs-member comparison passed.

## Installation and bounded test

Installed manual/one-shot-capable entry: **HarmonyOS 041 - GPU pipeline - AUTO RETURN 7 MIN**. It shares the preserved 031 kernel/DTB and 032 base initrd; the second initrd changes only outer init and composer. Overlay size 343,524 bytes; SHA256 `ee5f4afca0cb5f5ec2720bb12768726968e1744e6b6739a816b62e7a19a501fe`. All 102 preexisting EFI file hashes and Ubuntu default were preserved. No files were deleted.

One unique operational attempt ran from 18:08:47 to 18:14:09 UTC on 2026-11-12 and automatically returned to Ubuntu boot `40021852-61a9-4f14-9e38-966ebb4dffa2`. The ordinary target budget is 240 seconds, with a separate 420-second software reboot deadline and `panic=15`. A wedged kernel is not covered by a software deadline. The target ran to its timeout and the retained log records namespace termination and `NATIVE_ORIGINAL_END`.

The installed code retains SELinux support and the previously authorized permissive target mode. Ubuntu security and host display configuration were not changed. Physical touchpad/click acceptance, incomplete status-bar diagnosis, interactive desktop FPS and stable 120 FPS remain unverified.

## Review

Inline review checked PRIME versus DUMB destruction, partial-allocation cleanup, context migration, back-buffer ownership, real completion before input release, CPU fallback and actual MMI ownership. No subagent was used under the lightweight project workflow. Runtime evidence, rather than the offscreen probe, must establish that the original UID 3036 composer actually selected and executed GPU composition.

## Original-service result

The new run is `native-interactive-041-c098cd09-5e9f-47a2-8cbc-030748b91c41`. All 71 retrieved files match their remote hashes. Extraction mounted the original LAB read-only with `noload`, performed no journal replay, and unmounted it afterward.

Original composer PID 1023, UID 3036, logged `gpu_scanout_ready041 value=1`. Its bounded timing capture contains 32 successful `composer_gpu_two_pass041` records and no CPU fallback records. This establishes execution by the original service under HarmonyOS, not merely the root Ubuntu probe. Actual target SELinux samples report `enforce=0`: permissive, not disabled.

| Captured stage | 034 NEON baseline | 041 GPU |
| --- | ---: | ---: |
| Full composition scope, mean | 22.061 ms / 43 samples | 4.148 ms / 32 samples |
| Full composition scope, median | 21.526 ms | 4.192 ms |
| GPU two-pass scope, mean | not present | 4.111 ms |
| GPU two-pass scope, p90 | not present | 6.222 ms |

The full composition scope improved approximately **5.32×** (81.2% less time). Counters were deduplicated by complete timing tuple; the trace is capped, includes startup/idle work and does not represent sustained interactive throughput. First-frame work reaches 15.441 ms. `glFinish`, the upstream EGL submission and KMS presentation still have costs. **Stable 120 FPS is not demonstrated.**

The continuous fault collector made 25 samples and captured no fault file. No `NotifyWindowStateErrorFromMMI` or `CloseUIAbilityBySCB` appears in this run's hilog; neither application was physically exercised, so this is not application-repair acceptance. No physical cursor event was injected or inferred.

Supplementary offscreen 042 tested the actual helper across 32 RGBA/RGBX/BGRA/BGRX crop, scaling and edge-cursor cases, rejected invalid crops, and checked retained background. All RGB comparisons passed on the real FD690. That probe performed no KMS modeset and is not an additional HarmonyOS boot test.

After return, source/artifact tests passed again. Ubuntu remains current/default with no one-shot, firmware entries unchanged and automatic screen-off active. All 101 immutable old EFI files remain hash-identical. The only post-boot old-file difference is `loader/random-seed`, legitimately rotated by systemd-boot; it was not restored. The installed overlay hash remains correct. See `gpu-runtime-analysis.json` and `post-return-verification.json` under `native-original-graphics-boot-041/`.
