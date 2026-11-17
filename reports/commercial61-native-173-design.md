# Persistent diagnostic history and explicit teardown 173

Continue from the offline-recovered source data of operation 171 and the original
desktop/service baseline, preserving original images and Ubuntu default.

## Differential Fix

Boot 168's old collaboration checkpoint log prevented the unchanged noclobber
script from running. The early Home launcher then exited with HOME_GATE_FAILED.
The 168 checkpoint snapshot contains an earlier boot's event, so it is not
current-boot readiness evidence. Other adaptation-owned exclusive diagnostic
logs and FIFOs also need a per-boot lifecycle now that /data persists.

The 173 runtime inherits all prior six diagnostic-object archives and additionally
archives eleven explicitly named regular diagnostic files and two possible FIFOs
into the current boot's unique history directory. It uses no-follow stat checks,
single-link/type checks, collision refusal, rename and directory fsync. It does
not open/read FIFOs, remove files, reset app data, touch application databases,
change original service configuration, change readiness conditions or introduce
another Home/OOBE launch. Old checkpoint scripts and original authentication
remain unchanged. Fresh execution must still observe the genuine original event.

The outer lifecycle uses the tested 172 namespace pin, verified target reaping,
leaf-first alias/descendant unmount and zero-remaining-mount gate before backing
file and LAB sync. This is explicit data-mount cleanup, not a claim of graceful
original-service shutdown; target lifetime remains a bounded diagnostic.

## Admission And Verification

Admission passed eighteen focused scripts, reproducible static ARM64 builds,
guard refusals, the exact two-member init/early-wrapper delta against 164 and
complete 29-archive reconstruction. Original drivers, bootstrap, SceneBoard
launch scripts and diagnostic-channel payloads remain unchanged. The staged
runtime differs only in persistent storage/history support.

A host regression fixture reproduces the old-log/FIFO failure and then runs the
same checkpoint script successfully after archival using an explicitly synthetic
current-event fixture. That is parser/lifecycle testing, not native readiness.
Separate real WSL mount tests cover alias teardown and entering a pinned mount
namespace after its target is reaped. Native behavior must be verified separately.

Required native checks: current marker follows 168, real writable NVMe data mount,
original init handoff, six original diagnostic archives plus measured extra
archives, actual target/namespace identity, complete unmount and flush, independent
offline fsck clean, and preserved archived checkpoint log. SceneBoard/process/frame
observations are reported separately; no physical input acceptance is inferred.

Installed experimental entries are 168/173 after archived removal of 167. Original
manual entry, shared payloads and Ubuntu default remain. Operations are immutable,
single-attempt and bounded; target-side mount/retrieval/preservation checks remain
serial. Overall basic-driver goal remains active, prioritizing touch and USB.
