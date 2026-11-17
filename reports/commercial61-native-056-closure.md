# Commercial native 056 closure

One bounded boot ran 2026-11-14T16:27:01.664338Z to 16:30:43.572617Z,
returning to Ubuntu boot e8a388d0-5d18-45fd-be50-caeaaf2b7fa5. All 64 retrieved
files matched hashes, with read-only/no-replay retrieval. The real desktop
remains unverified; all seven sparse scanout PPMs were black.

## Screen Drawing Boundary

192 successful hardware event attachments; zero failures, lost samples,
malformed records or instruction mismatches. There were 178 intentionally
suppressed sample log lines, so printed records are incomplete. Hardware and
parsed sample counts agree for these observed thread lifetimes:

| Boundary | Counter/parsed | Logged | Logged after SceneBoard flush |
| --- | ---: | ---: | ---: |
| Worker Render non-null-root branch | 288 | 199 | 14 |
| Screen Drawable OnDraw | 288 | 199 | 14 |
| Screen Drawable RequestFrame | 1 | 1 | 0 |
| ComposerAdapter CommitLayers | 1 | 1 | 0 |

All these logged samples came from global TID 1549. RequestFrame was observed
at 74.831176846 seconds and CommitLayers at 74.838033408 seconds. The last
Composer frame was at 74.880067 seconds, before SceneBoard's first ArkUI flush
at 79.207 seconds. There were no recorded post-flush Composer frames. The
original screen drawing method is reached after flush, but no later frame
requests or layer commits were observed at these sites. This narrows the next
inspection to its early return branches, not a claimed missing GPU submission.
Periodic attachment and possible alternate paths still limit absence claims.
The target reached configured timeout/exit 9 and the observer stopped.

## Preservation

Offline ring/memory/specification tests passed; the archive differs from 045
only in init, retaining original bootstrap/userland/modules. Ordered overlays
and workflow safeguards passed. Ubuntu current/default, enabled/active screen
off timer, original manual entry, firmware and four original images passed
return verification. 118 prior EFI files matched except normal random-seed
management and archived, authorized removal of entry 054. Shared payloads were
preserved. Entries 055/056 remain. Retention stamp: 20261114T162650767513Z.

## Next

OnDraw has a common original reason-code store at VA 0x41f3b4, where w9 is
the reason; the separately stored early reason 33 starts at 0x41f240, and the
missing-parameters branch starts at 0x41f250. Its own screen-specific power
skip call returns to 0x41f504, with the original bool result in w0. Observe
these register/branch sites without reading or changing private objects. A
main-thread power-skip result from 055 does not prove the screen-specific
result is identical. Do not repeat the permission-denied public tree dumps.

Sources: commercial61-native-056/{boot-observation.json,hwbreak-analysis.json,
render-analysis.json,runtime-analysis.json,hwbreak-test.json}; runtime-evidence
retrieval manifest; commercial-return-audit-056/result.json.
