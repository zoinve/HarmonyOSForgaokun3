# Native landscape and genuine GPU execution — trials 023/024

## Outcome

- The HarmonyOS adaptation now advertises **2560×1600 logical landscape** by default. Original RenderService creates a screen node at that size. The composer actually rotates pixels clockwise into the physical **1600×2560** panel; its real 120 Hz panel timing is unchanged. This is not a relabelled portrait buffer.
- Genuine hardware GPU execution is verified: original RenderService, UID 1003, reports `FD690`, `freedreno`, `OpenGL ES 3.2 Mesa 25.0.1` from its active context. Kernel MSM GPU execution accounting increases from 3,307,704 to 246,209,060 ns in 023 and from 3,380,258 to 295,637,484 ns in 024. Loading a library alone was not used as proof.
- Animation has a **software presentation bottleneck despite hardware rendering**. The original reference bridge synchronously reads GPU pixels back to CPU memory; the composer then copies/rotates those pixels into a linear scanout buffer.

## Measured improvement, not an FPS claim

All values below are microsecond-derived milliseconds, medians of distinct original-process records, deduplicated across repeated trace-file dumps.

| Stage | 023 | 024 | Samples per trial |
|---|---:|---:|---:|
| Composer copy and rotation | 122.317 ms | 28.644 ms | 43 |
| EGL complete copy-frame scope | 37.871 ms | 35.694 ms | 63 |
| GPU readback/finish scope, nested inside EGL copy | 17.4595 ms | 15.6055 ms | 64 |

024 changes **only the composer transfer strategy**: bulk-copy the validated source DMA mapping into reusable cacheable RAM, run the tested tiled rotation there, then bulk-copy output rows into scanout memory. Original DMA-BUF START/END ownership transitions, fences, failures, pixel formats, crop/scaling and destination padding are preserved. The existing composer mutex serializes reusable buffers. Pixel-equivalence tests cover both formats, varying dimensions/crops, padding, buffer reuse and address/undefined-behavior sanitizers.

The measured composer-stage median is **4.27× faster (76.6% lower)**. EGL timing differences are incidental cross-trial variation, not a claimed EGL optimization. Readback scope is nested: do not add it to the complete EGL scope. Flip-scope records mix immediate no-pending returns with actual waits, so their median is not a refresh interval. Timers are capped startup samples, not a frame-rate benchmark. No claim of smooth 60/120 FPS is made; 120 Hz has only an 8.33 ms frame budget. A subsequent major optimization would replace synchronous readback/CPU copies with a real GPU DMA-BUF composition/import path, preserving actual buffer formats, modifiers and fences.

## Actual images and input limitations

- [023 captured physical scanout](native-original-graphics-boot-023/scanout-sample-11.png) shows the landscape lock screen rotated into the portrait-addressed panel.
- [024 captured physical scanout](native-original-graphics-boot-024/scanout-sample-11.png) shows the unlocked wallpaper and bar, also rotated into the physical panel. These files are real 160×256 downsampled RGB captures, not synthetic screenshots or a resolution claim about the capture itself.
- Both original logs contain `usual.event.SCREEN_UNLOCKED`. Original service identities are preserved. No authentication checks were bypassed.
- Human touch-coordinate alignment after rotation has **not** been verified. The inherited diagnostic input gesture was deliberately unchanged in 024 to isolate the performance change. Full desktop completeness, application usability and subjective animation smoothness remain unverified.

## Verification and preservation

Exactly one physical boot each of 023 and 024; neither completed experiment was rerun. Both returned automatically to Ubuntu. All **106 raw snapshot hashes**, original UID/domain samples, 12 target SELinux-permissive samples per trial, real RAM data mount and original read-only image loops pass independent verification. All three original SDK image SHA256 checks remain intact. Ubuntu LSM remains `capability,landlock`; target permissive mode is not a change to Ubuntu security.

024 returned Ubuntu boot ID `f18badba-800d-4456-b81a-5a2dd74a301f`. Default Ubuntu entry, cleared one-shot state and automatic screen-off timer were verified. The LAB partition is restored read-only/noload. No old logs, original SDK images, retained staged candidates or unrelated Ubuntu entries were deleted.

EFI reclaim was limited to unreferenced duplicate `native-original-graphics-013/initrd.img` for 023 and `native-original-graphics-014/initrd.img` for 024, each journalled and matched against the retained original staged file before deletion. Other static EFI hashes remained unchanged; normal systemd-boot random-seed rotation is separately recorded. 024 leaves 95,535,104 bytes free on ESP. Its counted entry filename and actual initrd are **024**, but its inherited cosmetic title still says trial **023**; install evidence retains this discrepancy rather than rewriting history.

These are guarded adaptation boot candidates, not a change to Ubuntu's display settings or persistent default boot. Original images remain untouched; the overlays and experimental data are volatile by design.

## Sources and evidence

HarmonyMac's pinned real EGL/composer path remains the implementation base; original reference files were not edited. The other two required references remain integrated: L410 HarmonyOS Adaptations supplies the previously verified local-storage compatibility/ABI design, and L410 Linux Compatibility Platform supplies dependency/FD architecture context. No unrelated platform replacement was introduced for these tasks.

- `next-experiment/build-native-original-graphics-boot-023.py`
- `next-experiment/build-native-original-graphics-boot-024.py`
- `next-experiment/native-landscape-copy-023.h`
- `next-experiment/native-cached-copy-024.h`
- `next-experiment/verify-native-landscape-performance-023-024.py`
- `reports/native-landscape-performance-023-024-verification.json`
- Both numbered directories retain source, compiler logs, manifests, staged guard results, install/boot journals, raw snapshots and independently reconstructed PPM/PNG images.
