# Commercial native 059 closure

## Result

One bounded boot ran 2026-11-14T17:04:51.513588Z to
2026-11-14T17:08:33.479238Z, returning to Ubuntu boot
2c0a99a4-77d2-44f6-9978-77b7b3667461. All 64 retrieved evidence files matched
remote hashes with read-only/no-replay access. Configured timeout and exit 9
were observed; the hardware observer stopped. Seven sparse captures remain
black. No authentic desktop or interaction is established.

## Actual Integration Change

The RAM-only board parameter file appends exactly
`rosen.uni.partialrender.enabled=0`. Original property-reading code and the
read-only literal addresses were verified against the original base ELF.
Pinned upstream supporting source identifies mode 0 as disabling partial
rendering; its visitor disables operation dropping for this mode. Source
commit and hashes are in commercial-partial-render-audit-059/result.json;
this is not a commercial-binary identity claim.

The exact original integer getter returned x0=0 in all 581 logged samples,
including 150 after the first SceneBoard ArkUI flush at 84.858 guest seconds.
There were 288 logged original RequestFrame entries and 288 CommitLayers
entries, with 75 of each after that flush. Hardware counters were respectively
749 for the getter and 372 for each drawing boundary. Screen-node-skip result
had no samples or counter hits, consistent with its original gate no longer
being taken. 204 attachments, zero failures/lost/malformed/IP mismatches;
336 suppressed sample log lines mean logs are not a complete event accounting.
Periodic thread attachment still limits complete execution coverage.

Composer recorded two post-flush frames, the last at 120.054478 guest seconds,
where 058 had none. Both source and output sparse pixels were black. Thus the
public parameter advances the real original frame/commit path, but does not
solve missing desktop content. Do not present this as desktop success or infer
all 75 commits reached physical scanout from the entry probes alone.

## Preservation

The full candidate differs from 045 only in init and the board parameter file;
the latter equals the previous bytes plus the single line. Original service
binaries, bootstrap and modules retain their bytes. Public parameter mutation
is explicitly distinguished from binary preservation in test admission.
Ring/memory/specification tests, exact audit/test equality, workflow guards
and ordered overlay/full-archive equivalence passed before installation.
The overlay allow-list initially rejected the added parameter, before any
overlay was emitted; it was updated to require this exact additional member.

Ubuntu current/default, original manual entry, firmware, all four original
image hashes, unmounted lab partition, and screen-off timer enabled/active
passed. 121 prior EFI files matched, accounting for the normal random seed
and hash-archived removal of entry 057, retention 20261114T170443195420Z.
Entries 058/059 and all shared payloads remain. No original authentication,
tokens, identities, sandbox checks or OOBE state were changed.

Next preserve the proven full-render configuration while observing actual
original surface/canvas/content traversal, rather than treating absent
presentation as the remaining problem or replacing native Adreno libraries
without evidence. Do not rerun 059.

Evidence: commercial61-native-059/{boot-observation,hwbreak-analysis,
render-analysis,runtime-analysis,full-render-analysis,hwbreak-test-revision2,
partial-render-provenance,overlay-result}.json, runtime-evidence manifest,
commercial-render-audit-059 and commercial-return-audit-059.
