# Original memory-service initialization failure: evidence correction 110

No target boot, kernel change, original image modification or service change in
this investigation. Goal remains a real stable interactive native desktop.

## Correction to 109 closure

The 109 closure incorrectly stated that the available evidence could not
distinguish Init failure from Publish failure. The DFX stacks alone cannot, but
the preserved 109 original HiLog already contains decoded memory-service logs.
That evidence was overlooked during the earlier stack-focused review.
Keep the old report and raw evidence unchanged; this report supersedes that
specific conclusion, not the preservation or capture results.

Hash-verified original log:
`4f0d40a53029c407ba3c696097ce049222390d704e45ccd3ebc7abe8d9744b40`.
At guest pre-sync time 01-01 08:00:20.178, PID467/TID486 reports, in order:

1. Writing 300 to `/dev/memcg/memory.app_score` failed.
2. Writing Root to `/dev/memcg/memory.name` failed.
3. `/dev/memcg/memory.zswapd_single_memcg_param` was not found.
4. `Init init failed`.
5. `Init ReclaimStrategyManager init failed`.
6. `OnStart init failed`.

Raw byte-line numbers: 2162, 2166, 2167, 2169, 2170, 2171. The entire sequence
has one PID/TID/timestamp. First DFX snapshot is 55 ms after the failure, which
explains why the snapshot shows the Binder work loop instead of initialization.
Original OnStart disassembly establishes that Init false skips Publish.
Low-level errno/individual function return registers were not captured.

Together with the service namespace survey, this establishes a failing original
memory-service initialization path that encounters the empty ext4 bind instead
of the required memory-controller interfaces. It does not establish that fixing
memory initialization alone will stop OOBE recovery or prove desktop completion.

Detailed analysis: `memmgr-init-failure-analysis-110.json`.

## Exact kernel and reference differences

Actual experimental kernel045 and configuration hashes match the installed
kernel recorded in the boot workflow. MEMCG is enabled; MEMCG_V1 is not.
Inspected memcontrol and legacy memcontrol sources do not define app_score or
zswapd_single_memcg_param. Enabling upstream memcg v1 alone is insufficient to
provide those vendor extensions. Source/config hashes are recorded in
`real-memcg-requirements-audit-110.json`.

HarmonyMac `ports/tools/prepare-init-service-test.sh` explicitly labels its
regular-file memcg placeholders diagnostic-only. The fixture writes zero to
the missing names. This is a relevant reference technique for its fixture, not
proof of real memory-controller behavior or of the native desktop runtime.
No such placeholder files or fake memory statistics were installed here.

## Logging audit

The earlier SDK decoder is not the current commercial-image decoder. Extracted
the genuine supplied hilog, libhilog.so and hilogd read-only, with hashes and
original mini-symbols under `commercial-hilog-audit-110/`.

Original `hilog -d /system/lib64/libmemmgrservice.z.so` is a supported single-ELF
dictionary request. Daemon handler validates ELF and generates the dictionary.
CLI zero exit alone does not establish generation success. Verified build-ID to
dictionary mapping for UUID3036376538 and the expected dictionary path.

108 has 127 failed MM decode messages without original format IDs/argument
payloads in their text. They were not reconstructed. In contrast, 109 already
has 129 decoded MM messages, including the decisive initialization sequence.
The failed first contract-audit assertion exposed this difference before any
output directory was created; the corrected audit explicitly handles both runs.
No operational experiment was repeated.

The prepared original dictionary observer has five passing checks, but is
deferred: another dictionary-only boot would not discriminate the now-known
failure. It has not been integrated, installed or executed on the target.

## Next implementation boundary

Investigate a genuine memory-controller adaptation or a verified supported
original nonvendor mode. Do not simulate controller files/metrics, fake service
publication, patch original binaries, remove token checks or synthesize setup
completion. A real fix still needs an admitted candidate, bounded boot, original
SA publication, desktop query timing, OOBE outcome, full pixels and visible input
response, with all Ubuntu/image/security preservation gates retained.
