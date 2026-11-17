# Commercial native 061 closure

## Result

One bounded operational boot ran 2026-11-14T17:27:19.540729Z to
2026-11-14T17:31:01.281085Z. Run identifier:
commercial61-native-061-e43ccf25-0d16-4d07-9550-350a1f1fd89d.
All 64 retrieved files matched remote hashes, with read-only/no-replay retrieval.
Configured timeout/exit 9 and stopped observer were recorded. Seven sparse
captures remain black. Authentic desktop pixels and interaction are not achieved.

## Original Command Execution

188 attachments; zero attachment failures, lost samples, malformed records or
instruction mismatches. 2618 sample log records were suppressed, not lost from
the perf ring. First SceneBoard flush was at guest 80.224 seconds.

| Original helper | Logged samples | Hardware events | Logged after flush |
| --- | ---: | ---: | ---: |
| AttachToUniSurfaceNode | 2 | 2 | 0 |
| AddChild | 512 | 1849 | 128 |
| UpdateRecording | 41 | 41 | 6 |
| UpdateModifierNGDrawCmdList | 414 | 1695 | 130 |

All 41 UpdateRecording samples belong to genuine SceneBoard PID 3546 node IDs,
covering 17 nodes. Original command-dispatch callsites were audited. Helper
entry does not prove successful node lookup or subsequent command completion.
The genuine SceneBoard root is 15229954031618. Two ordinary root/surface attaches
belong to EngineService and startupguide, not SceneBoard. Absence of a logged
ordinary SceneBoard attach is not proof of an absent root; its architecture can
use another path. Suppressed edges do not form a complete/current tree. Original
RS logs place SCBWallpaper and SCBDesktop on tree.

Three composer frames followed the first flush, last at 120.054573 seconds;
their source/output sparse samples remain black. The supported full-render
parameter from 059 remains enabled (rosen.uni.partialrender.enabled=0).

## Next Evidence Boundary

Original hilog explicitly names BootAnimationNode in surface OnDraw at 47.606,
54.484, 72.542, 77.019, 84.482 and 120.020 seconds. The genuine bootanimation
process logs completion at 73.431 seconds and successfully sets
bootevent.bootanimation.finished at 73.442 seconds. Original consumers return
success waiting on that parameter at 73.448 seconds. PID 860 still emits
watchdog messages later. The boot surface node ID is 3693671874563.

This is evidence of continued drawing after reported completion, not yet proof
of stale-surface occlusion or a causal cleanup failure. Do not fabricate boot
completion, kill the process, detach a node or inject a desktop root. Compare
original completion/destruction and render-tree visibility paths first.

## Preservation

Return verifier completed successfully, Ubuntu boot ID
4e45e150-f950-4cfa-a1fd-327eb165080d. Ubuntu current/default, original manual
entry, firmware, four original image hashes and enabled/active screen-off timer
passed. Lab partition is unmounted. 123 prior EFI files matched; random-seed is
the normal boot-managed change. Entry 059 was hash-archived before authorized
removal at retention stamp 20261114T172708408583Z. Entries 060/061 remain.

Build/observation/overlay tests passed. Archive differences from 045 are exactly
init and the single-line-appended board parameter file. Original service
binaries, modules, bootstrap, identity/security checks and OOBE state remain
unchanged. Observation used register-only hardware execute breakpoints, without
private-object reads or instruction replacement. Do not repeat completed 061.

Evidence: commercial61-native-061/tree-analysis.json, hwbreak-analysis.json,
render-analysis.json, runtime-analysis.json, post-return-verification.json,
runtime-evidence/retrieval-manifest.json and commercial-command-dispatch-061.
