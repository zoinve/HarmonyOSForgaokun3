# Commercial native 058 closure

## Result

One bounded boot ran 2026-11-14T16:52:37.823066Z to
2026-11-14T16:56:19.632728Z, returning to Ubuntu boot
b7a1107a-21c7-4c59-aa9d-28dcaa91efd3. All 64 retrieved files matched remote
hashes, with read-only/no-replay access. Configured target timeout and exit 9
were recorded; the observer stopped. Seven sparse 160x256 captures remain
entirely black. Desktop and interaction are not achieved.

## Original Branch Results

192 attachments, zero attachment failures, lost samples, malformed records or
instruction-pointer mismatches. There were 88 suppressed sample log records;
the two active hardware counters each counted 307, while each logged 263
samples. All samples were on global TID 1614. Periodic attachment still limits
complete thread-lifetime coverage.

- SkipFrame return: 263 logged samples, all x0=0.
- CheckScreenNodeSkip return: 263 logged samples, 259 x0=1 and four x0=0.
- Processor creation failure and processor initialization failure stores:
  zero samples and zero counter hits.
- After the first SceneBoard ArkUI flush at 73.846 guest seconds: 32 logged
  returns from each active site; SkipFrame always false and CheckScreenNodeSkip
  always true. No post-flush Composer frames were recorded; the last was at
  72.067945 seconds.

The actual original OnDraw code branches on the CheckScreenNodeSkip bool and
stores reason 21 at VA 0x420a08 for true. This identifies an observed dirty/
screen-skip path, not the ultimate cause of missing visible desktop buffers.
The upstream helper can either skip commit or perform hardware-only commit
before returning true. Do not equate every true return with no internal commit.
The independent Composer evidence records no post-flush frames here.

## Preservation And Tests

Ubuntu current/default, timer enabled/active, original manual entry, firmware,
and all four commercial image hashes passed. 120 prior EFI files matched,
accounting for the normal random-seed change and hash-archived removal of
entry 056 (retention stamp 20261114T165225714430Z). Entries 057/058 and shared
payloads remain.

The first offline test report has a metadata-only address corruption inherited
from a broad synthetic fixture replacement. Preserve that report. The actual
build/audit address was correct. Corrected revision2 test passed, including x9,
and exact specification equality with the audit was required before install.
Original executable mapping comparison was read-only; no original instructions
or private-object state were changed. Only init differs from base 045.

Next: audit the original public integer rendering property and supporting
upstream enum, then test a separately numbered full-render configuration if
the binary's original parameter path supports it. Do not mutate private flags,
replace the desktop, fake completion, or bypass original permission checks.

Evidence: commercial61-native-058/{boot-observation,hwbreak-analysis,
render-analysis,runtime-analysis,hwbreak-test-revision2}.json,
runtime-evidence/retrieval-manifest.json, commercial-render-audit-058/result.json,
commercial-return-audit-058/result.json.
