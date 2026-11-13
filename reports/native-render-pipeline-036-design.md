# Candidate 036: GPU composition probe and possible pipeline replacement

User authorization includes redesigning the rendering pipeline if necessary, without interrupting unattended work. Preserve original HarmonyOS services, Binder semantics, identities, Ubuntu default startup, timed return and numbered evidence. The three pinned reference projects remain architectural constraints, not permission to substitute a Wayland desktop or private-function success tests for real RenderService integration.

## Evidence and decision boundary

034 reduces real copy/rotation time from 28.42 to 22.06 ms, still well above 8.33 ms. 035 isolates DMA read, NEON rotation and scanout publication. Do not redesign based solely on the cached-memory microbenchmark. A GPU-only offscreen probe will establish pixel correctness, FD690 execution, DMA import/renderability and synchronization before changing the original compositor path.

## Proposed native GPU path

Keep the original HDI composer contract and existing KMS back-buffer/page-flip lifecycle. Import the real client DMA-BUF into EGL, rotate using exact texel fetches into an owned GPU background texture, then compose that background and the actual MMI cursor into the non-front scanout DMA-BUF. Keep the background independently of the released client so idle pointer motion never accesses a returned client buffer. Do not fabricate a RenderService cursor surface or alter input events.

An EGL context must be bound and released under the existing compositor mutex on each submitting thread: both commit and the idle cursor worker may use it. Start with explicit completion (`glFinish`) for correctness and measure it; native fences can replace that only after real lifetime and KMS synchronization validation. GPU writes must not be falsely described as CPU DMA ownership. Preserve tested NEON fallback and truthfully log any failed import, shader, framebuffer or renderer check.

A prototype must check full output pixels against CPU reference patterns, both rotation and cursor visibility/edges. A root-owned offscreen Ubuntu diagnostic can prove hardware capability but not HarmonyOS service credentials, linker namespaces, compositor integration, physical cursor input or desktop FPS. The target bootstrap already assigns real DRM nodes to graphics group 1003, and the original composer supplementary groups include 1003; no credential modification is proposed.

Do not select a new target candidate until geometry/color/fence tests pass. A bounded HarmonyOS integration must then show the real desktop and original service lifecycle under the same automatic-return safeguards. Stable 120 FPS and physical click acceptance remain separate, unmet acceptance criteria. Status-bar geometry is unchanged pending visual evidence.
# Measured allocator boundary (040)

The bounded Ubuntu offscreen 040 test passed exact full-frame RGB, rotation,
corner cursor and hide checks on FD690 using GBM-owned linear buffers. Two
passes plus glFinish averaged 3.68658 ms at physical 1600x2560. Earlier DRM
DUMB import tests failed; exact driver-internal causality remains unknown.
This proves capability, not original HarmonyOS service integration or FPS.

041 therefore uses GBM-owned scanouts with PRIME imports into the existing KMS
card. PRIME-import GEM handles must be GEM_CLOSE'd, never DESTROY_DUMB'd.
Original DUMB allocation remains the initialization fallback. GPU rendering
imports the actual client FD, retains an independent GPU background, and
finishes work before releasing input or page flipping; idle cursor updates
must never read the previous client FD. Bind/unbind EGL under the existing
state mutex allows safe context migration between commit and cursor threads.
