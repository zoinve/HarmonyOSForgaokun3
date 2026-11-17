# Native desktop experiment 108 closure

## Scope and execution

One installed candidate, one boot, one read-only noload retrieval. Do not rerun.
Run: `commercial61-native-087-8a623718-eb63-405e-870b-7a0417a16c03`.
Boot request: 2026-11-15T16:47:33.836273+00:00.
Ubuntu return: 2026-11-15T16:51:17.825718+00:00.
Returned boot ID: `e224118b-e3a1-44a8-bb70-71f0c199fcd2`.

Only behavioral change: create directory prerequisites for the supplied original
memory-service namespace wrapper before original init. No replacement service,
fabricated metrics, identity, activation or setup completion; no original binary
patches. The installed runtime path and both runtime hash checks used 108.

## Findings

- All five required directories were genuinely absent and created with mode 0755.
- Unlike the earlier wrapper zombie, original `memmgrservice` now executes:
  original HiLog records namespace PID 381 setting its process name, starting
  FFRT queues and continuing through the late observation window. This supports
  launch-chain progress, not service readiness or successful initialization.
- Original CheckSystemAbility probe reports SA 1909 absent with status 2 at all
  seven targets: 20, 40, 60, 80, 100, 120, 140. Monitor completed.
- SceneBoard query remains slow: 15085 ms; server request to stage1: 9080 ms.
  Both original DFX captures overlap the query and request. DeviceManager PID
  757: 23 threads, 242 frames; CollaborationFwk PID 962: 81 threads, 904 frames.
- Original memory service emits an accessToken IPC failure early in startup,
  FFRT kernel-feature warnings, and many undecoded original log records.
  These are observations, not yet a proven reason for failure to publish SA1909.
- Reference force-stop command succeeds, but original guide relaunch remains.
  Guide PID 9095 owns focused window 72 at targets 90, 110, 130, 145;
  SceneBoard PID 4696 is present at those samples. Desktop not achieved.
- Original target bounded exit is recorded: timeout=1, PID 438, status 9.

## Pixels and interaction

Both 120/140-second frames contain all 2560x1600 source pixels and exact clockwise
1600x2560 output rotation. Frames differ at 11833 pixels. Image-view tool rejects
input; no visual inspection performed. OCR is unreliable, not desktop evidence.
Keyboard events reach SceneBoard 4696, but visible response is not established.

## Preservation and analysis

134 retrieved files matched remote hashes; partition unmounted after retrieval.
All four original images and firmware unchanged; Ubuntu current/default, original
manual entry and enabled/active screen-off timer preserved. Archive
`boot-entry-retention-20261115T164719625061Z` removed only 105, retaining 107/108.
160 prior EFI files unchanged; normal loader random-seed update accounted for.
Credential audit scanned 134 files / 386508820 bytes with no credential export.

Analysis parser now anchors full end-marker lines and requires the complete
seven-target sequence plus observer completion before claiming all-sample success.
Four focused parser regression tests passed. Initial pixel review ran before PNG
generation and failed without creating a review report; after generation the
review completed once successfully. No operational experiment was repeated.

Authoritative details: `commercial61-native-108/memmgr-runtime-analysis.json`,
`server-event-analysis.json`, `reference-runtime-analysis.json`,
`post-return-verification.json`, `post-return-review.json`, and retrieval manifest.

## Next work

Keep the full desktop goal active. Investigate original memory-service internal
initialization and original diagnostics; directory scaffolding alone is not the
solution. Do not remove token checks, synthesize SA1909, fake setup completion,
or infer an OOBE bypass from memory-service progress.
