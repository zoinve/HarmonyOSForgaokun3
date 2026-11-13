# Native 2560x1600 stable 120 FPS target

The user now requires stable **120 FPS**, not merely a 120 Hz panel mode or improved average CPU timings. Keep the original services, genuine hardware operations, identities and error reporting. Preserve Ubuntu default boot, automatic screen-off and all numbered evidence.

024 does not satisfy this target: its composer CPU rotation alone has a 28.6 ms median, and EGL still reads pixels back. The next changes remove these costs in separately evidenced candidates:

1. 025: import actual NativeWindow DMA-BUFs into GPU framebuffer objects; blit the rendered image without CPU readback. Export real native release fences; label any synchronous fallback explicitly. Preserve application GL state and the original queue/fence contracts.
2. Next: GPU composition/rotation into real KMS-compatible buffers instead of the remaining CPU rotation, with actual synchronization and pageflip events.
3. Measure actual completed presentations during sustained, changing desktop animations. Record refresh sequence, unique frame identifiers, presentation intervals, misses, latency and thermal/clock behavior. An average stage timing, repeated frames, submission timestamps or a mode label cannot certify 120 FPS. Separate startup from steady state and test a sustained workload before any stability claim.

No guarantee that arbitrary applications can render at 120 FPS is implied. Current status: **target not achieved**. Candidate 025 is an intermediate change, not completion of this requirement.
