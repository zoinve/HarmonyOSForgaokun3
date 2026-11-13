# Native GPU composer 041 implementation plan

**Goal:** Remove the measured CPU DMA readback from original HarmonyOS client composition while retaining real MMI cursor behavior and bounded automatic return.

**Architecture:** A self-contained GPU helper owns EGL/GBM and a clean background. The existing composer retains service ABI, KMS ownership, input-fence waits and page-flip lifetime. CPU NEON is the correctness fallback. Execute inline, no agents, commits or approval pauses.

**Spec:** `reports/native-render-pipeline-036-design.md`.

## Constraints and review focus

- Preserve original images, previous candidates/logs, Ubuntu default and screen-off timer; no service identity changes.
- Every new operational test has a unique number, one attempt and the 420-second software deadline; a wedged kernel is not recoverable by that deadline.
- PRIME imported GEM handles use GEM_CLOSE; DUMB handles use DESTROY_DUMB. GL references are released before underlying buffers.
- Bind and unbind the context on every serialized commit/idle repaint. Failed GPU work cannot leave stale background marked valid.
- Failed input imports fall back to CPU without claiming GPU acceleration. Scaling/crops must preserve the previous pixel contract.
- No previous client reads for idle cursor, front-buffer writes, fake fences, fabricated RS surfaces or synthetic input.

## Tasks

- [x] Add `test-native-gpu-composer-041.py` and a real pixel harness for the helper. First run failed for the missing header. Linux compilation and the bounded real FD690 offscreen harness passed RGB/corners/hide, released-input repaint and context migration. Results: `native-gpu-composer-test-041/result.json`; root diagnostic is not original-service acceptance.
- [x] Implement `native-gpu-composer-041.h`: runtime EGL/GBM resolution, FD690 validation, GBM scanout allocation, exact shader rotation/cursor, clean-background lifetime, synchronous completion and context migration via caller mutex. Destruction reverses image/FBO/BO/FD lifetimes.
- [x] Implement `build-native-render-041.py`: independently copy 034 composer, preserve adapters, add GPU scanout/commit/idle paths and explicit CPU fallback. Original hashes retained; actual AArch64 OHOS link with no undefined symbols passed. Read-only source/artifact test passed.
- [x] Build the unique original-service 041 auto-return candidate and tiny overlay over 032. Nine hashes and two native non-PID1 guards passed. Archive differences are only init and composer. Installation retained all 102 preexisting EFI files and Ubuntu default; overlay is 343,524 bytes.
- [x] Executed once and returned to Ubuntu boot `40021852-61a9-4f14-9e38-966ebb4dffa2`. Retrieved 71 files read-only with matching remote/local hashes and no journal replay. Original UID 3036 selected GPU scanouts and recorded 32 GPU frames; captured CPU fallback records: zero. The measured composition scope averaged 4.148 ms versus 034's 22.061 ms. Fault collection sampled 25 times without capturing a fault file. No interactive FPS or physical touchpad acceptance is inferred.

## Final verification and rulings

- Read-only artifact/source tests passed again after return; their conservative runtime flags describe the tests, while `gpu-runtime-analysis.json` records actual service execution.
- Original LAB is unmounted, Ubuntu is current/default, no one-shot remains, and the screen-off timer is active. Firmware entries and installed overlay hash match.
- Ruling: post-boot EFI comparison permits only `loader/random-seed` to change, because systemd-boot rotates it as part of normal boot security. It was not restored. All 101 other previously recorded EFI files remain hash-identical; installation itself preserved all 102.
- The supplementary real-GPU 042 harness passed 32 format/crop/scale/edge-cursor cases. It is an offscreen diagnostic, not a second HarmonyOS operational run.
- Author review only; no independent reviewer was dispatched under the project's no-ritual-agent preference. Physical cursor/click behavior, visible status-bar completeness, interactive presentation pacing and stable 120 FPS remain open.
