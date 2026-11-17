# Commercial native 060 closure

## Result

One bounded boot ran 2026-11-14T17:14:54.472136Z to
2026-11-14T17:18:36.402193Z, returning to Ubuntu boot
1352702e-d11f-40d2-b9c7-c437206d3696. All 64 retrieved evidence files matched
remote hashes, using read-only/no-replay access. Configured timeout/exit 9
and stopped observer were recorded. Seven sparse 160x256 captures remain
black; desktop and interaction are not achieved.

## Actual Drawing Boundaries

The public full-render configuration from 059 is byte-identical. Only init
differs from 059; the tests also require the exact two-member difference from
045 (init and the single-line-appended board parameter file).

188 attachments; zero failures, lost samples, malformed records or instruction
mismatches. There were 1178 suppressed sample log records. At global TID 1648:

- Surface OnDraw: 269 logged samples / 269 hardware events, one observed x0
  object address; 69 logged samples after SceneBoard's first flush at 76.870s.
- Adapter DrawChildren: 508 logged / 1097 hardware events, four observed x0
  object addresses; 96 logged samples after first flush.
- Adapter DrawContent: 508 logged / 1097 hardware events, the same four
  observed object addresses; 96 logged samples after first flush.
- Canvas OnDraw: zero samples and zero hardware counter hits.

The adapter functions can return for an empty command list or absent index;
entry observation does not prove an actual drawing callback was executed.
Object pointer equality is not a node-ID identification. No private objects
were dereferenced to name these objects. Zero Canvas OnDraw observations are
not proof that every possible drawable subtype/path was absent, nor complete
thread-lifetime execution coverage. In particular, do not claim that the one
surface was BootAnimation without authentic ID evidence.

Composer recorded three post-flush frames; the last was 120.046701s. Their
source and output sparse pixels were black. The 059 improvement to frame
production persists, but meaningful desktop content is still unresolved.

## Preservation

Ring/memory/audit metadata tests, original bootstrap/module preservation,
single-line parameter check, strict transport/timer/default/image guards, and
ordered overlay equivalence passed. Ubuntu current/default, enabled/active
screen-off timer, original manual entry, firmware and four image hashes passed
return verification; lab partition unmounted. 122 prior EFI files matched,
accounting for normal random-seed change and hash-archived removal of 058 at
retention 20261114T171445557096Z. Entries 059/060 and shared payloads remain.
No original service binary, authentication/identity, sandbox or OOBE state
was modified. Do not rerun completed 060.

## Next Actual Integration Boundary

Original SceneBoard logs set a genuine root rsId 14577119002626 at 45.393s,
with SetRootSessionRect [0 0 2560 1600]. Subsequent Canvas drawable execution
is not observed. Audit original root-to-surface attach, AddChild and real
drawing-command update helpers to correlate actual NodeId register arguments
with those service logs. Do not inject a root, fake completion or name object
addresses using guessed offsets.

The historical own-EGL diagnostics exhaust their pixel-readback quota before
the first flush. Existing pbuffer creation failures therefore remain an
unproven candidate, not a demonstrated explanation for post-flush black.
No speculative EGL replacement was made.

Evidence: commercial61-native-060/{boot-observation,hwbreak-analysis,
render-analysis,runtime-analysis,hwbreak-test-revision2,partial-render-provenance,
overlay-result}.json, runtime-evidence/retrieval-manifest.json,
commercial-render-audit-060 and commercial-return-audit-060.
