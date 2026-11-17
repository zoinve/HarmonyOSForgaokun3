# OOBE 116: gate early Home on an original collaboration checkpoint

Parent: completed 114. Evidence 115 establishes that in the same boot the
first SceneBoard blocked in a synchronous device query and was killed by
original AppMS, whereas the replacement SceneBoard's query returned in 7 ms
after an original collaboration initialization checkpoint.

Only the existing early Home launcher is gated. The helper waits for one
current CollaborationFwk PID and accepts that PID's original success log:
OnAddSystemAbilityEvent# RegisterHichainProofExceptionStatusCallback, ret: 0.
The helper rechecks PID identity after observing the log. This is a selected
checkpoint, not proof of complete service readiness. If service initialization
depends on Home/WMS, the bounded gate may fail; no fabricated fallback is used.

Gate bounds: up to 30 one-second process polls, then a 60-second event read,
with an outer 95-second timeout. Its private hilog reader is cleaned up. It
does not start/stop original services or modify identity, tokens, setup state,
trust lists, original binaries, kernel, watchdog or original recovery.

The existing early account initialization/retries remain otherwise identical.
The 114 reference script is unchanged: no second startup owner, original
guide wait, ten-second sleep and one aa force-stop. A possible independent
original Home launch remains observable and is not suppressed.

Changed archive members: native-target/desktop-order020.sh, the new
native-target/commercial-collaboration-ready116.sh, outer init log exporter,
and its integrity hash in early-hardware093.sh. Actual runtime remains
byte-identical at the verified 108 path. Original image bytes are unchanged.

Eight isolated executable gate tests passed. Full ordered overlay reconstruction
matches the complete archive; three isolated boot guards return 77. Inherited
installation, one-shot single boot, automatic return, read-only noload retrieval,
privacy checks and preservation verification remain. Keep latest two experiment
entry files only, archiving old contents/hashes first; retain shared payloads.

After one boot, verify current-PID checkpoint, launch order, first synchronous
query duration, guide stop and subsequent recovery, SceneBoard PID stability,
full-resolution pixels and real visible interaction. READY and process presence
are not acceptance. Missing pixels or uncertain interaction remain incomplete.
Never rerun the operational number or overwrite numbered evidence.
