# Native 067: Late Original Framebuffer Observation

## Result

The authentic desktop and interaction goal remains active, not achieved.
This is one completed operational boot, not authorization to repeat it.
Run: commercial61-native-067-0deb91c0-51de-4875-9354-6f59bbe843ee.
Boot observation: 2026-11-14 19:47:42.068388Z to 19:51:23.865900Z.
Returned Ubuntu boot: 65ba1e90-a166-4142-8048-70565e8cb6f5.

Only init and native-target/graphics016/system/lib64/libEGL_impl.so differ
from 066. The bootstrap and every other archive member are byte-identical.
The outer init change is the experiment name. The EGL change retains early
probes and adds independent five-second gates during monotonic [100,145).
It changes no rendering decision, original service, identity or provisioning.

## Actual Evidence

64 retrieved files match remote hashes; partition journal was not replayed.
SceneBoard first flush is 102.455 guest seconds. The complete presentation
trace is 50675 bytes, sample 29, EOF verified, SHA256
ae519f363f0a4bd6cc05782164e5424f83be41ef9ef0e989cdaaacf0d27cb036.
It reaches 150.332409 seconds and has 47 post-flush composer records with
nonblack sparse source/output samples. Composition did not simply stop.

Nine late observation rounds yield 18 readback records, source and destination
at 2560x1600. All report framebuffer complete, nine confirmed pixel writes,
and zero nonblack sampled points. Actual late frontend and Mesa queries
report matching current contexts, FD690, the same viewport and program state.
These records cover the original missing late interval. Nine sample points
are not a full image; they cannot prove every pixel is black or establish
that all original GL draw calls execute correctly. Composer's tiny nonblack
sample region and black GL sample points are not contradictory.

216 hardware observation attachments, no failures, lost/malformed records or
instruction pointer mismatches. 4657 log lines suppressed, not lost events.
The target exits under its normal diagnostic timeout; observer stops.

## Tests And Preservation

Compiled exact gate tests pass: time boundaries, clock failure/errno retention,
nine-round maximum and one winner among 32 simultaneous threads. Exact source
reversal recovers 035 EGL source byte-for-byte. Archive admission comparison
passes. The bridge cross-compiles with unchanged public exports and runtime
closure. No target-runtime success is inferred from the build alone.

Post-return verification passes: Ubuntu current/default, firmware, original
manual entry, all four original images, unmounted lab partition and screen-off
timer enabled/active. 129 prior EFI files unchanged; exceptions are the normal
random seed and hash-matched authorized removal of experimental entry 065.
Only experimental entries 066/067 remain; shared payloads were not removed.

The first return verifier overlapped the retrieval's temporary read-only mount
and correctly refused the unmounted-partition assertion. It was rerun after
retrieval/unmount and passed. This was not a second boot. A mistakenly selected
historical QEMU verifier refused at its existing-output guard before any QEMU
execution or output modification; the newly added incorrect wrapper was
removed. Historical numbered artifacts remain untouched.

## Reference And Next Boundary

See reference-oobe-resource-followup-067.md for the actual L410 rawfile path
interposition, HarmonyMac StartupGuide force-stop and Linux Compatibility
Platform scope. Neither private resource interposition nor force-stop was
loaded. Resource compatibility type audit is commercial-resource-policy-audit-067.md.

Next evidence must address full-resolution completed buffers and the original
RS draw/content path. Do not call sparse pixels a desktop, change device
identity based on the compatibility warning, fake package installation, stop
StartupGuide or mark provisioning complete. Do not rerun completed 067.
