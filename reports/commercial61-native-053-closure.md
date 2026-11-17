# Commercial 053 closure

The sole boot ran 2026-11-14T15:34:46.887137Z through
2026-11-14T15:38:28.807054Z, returning to Ubuntu boot
c8e5159e-2506-4a44-9b98-123d3efe0259. Do not repeat 053.
All 64 raw files match remote hashes after ro,noload retrieval; no original
partition journal replay occurred. Normal target timeout, target exit status 9
and observer shutdown before cleanup are recorded in phase-062.log.

## Observer and offline audit

053 retains the working 052 read-only executable-mapping verification and
register-only hardware sampling. It changes only the four observed sites:
unmarshal_result, recv_data, process_data and process_uni. The new result site
is original base ELF VA 0x3290a8, file offset 0x3280a8, instruction f44f42a9.
Both success and failure reach mov x0,x19 at 0x3290a4 before this epilogue;
x0 is the returned transaction object or null. There is no object dereference.
Original ELF hashes, executable segment translation, all entry instructions,
memory-comparison error paths and perf ring fixtures passed offline checks.
The complete specifications are in hwbreak-test.json. Full 053 differs from
full 045 only in init; original bootstrap, modules and userland are unchanged.
The incremental ordered archive chain equals full 053.

## Runtime evidence

There are 196 successful hardware event attachments and zero logged attachment
or mapping failures. Actual samples: unmarshal_result 60, all x0 non-null;
recv_data 49. No samples were captured for process_data or process_uni.
No lost, malformed, suppressed or IP-mismatch samples were reported.
Periodic thread discovery means these counts are not exhaustive call coverage.

Original SceneBoard installed and ran. Missing-application-agent warnings are
absent. First SceneBoard ArkUI flush is at guest 80.890 seconds; last Composer
frame is at 74.349895 seconds. After that first flush, 11 successful decode
results and 8 main-thread RecvRSTransactionData entries were sampled. No
post-flush Composer frame was observed. All seven exported 160x256 scanout PPM
images are entirely black. Real desktop pixels and interaction remain unproven.

This rules out a blanket claim that original UI transactions cannot decode or
reach the main-thread receive method. It does NOT prove that all transactions
decode, that each receive is non-null, or that any transaction was consumed.

## Correct interpretation of zero processing samples

Original RSMainThread::ProcessCommandForUniRender directly calls transaction
Process at VA 0x30f73c and may bypass ProcessRSTransactionData. More importantly,
the much larger original ProcessCommand implementation has its own indirect
transaction Process calls. LLVM 19 readelf decodes the original packed Android
relocations and identifies GOT 0x4bd7d0 as
RSTransactionData::Process(RSContext&). Original ProcessCommand loads page
0x4bd000 into x27 at 0x167fdc and its +2000-byte GOT entry at 0x168060, then
has blr x27 sites at 0x168424, 0x16891c, 0x16968c and 0x169b34.

Thus zero samples at the two standalone processing methods do not establish
failure to consume transactions. GNU readelf did not decode these packed
relocations; use the already installed llvm-readelf-19 for this audit rather
than interpreting its absence from GNU output as absent calls.

Next observations should target the actual transaction Process body and
ProcessCommand/render boundaries, preserving the proven read-only resolver and
original system behavior. No processing bypass, fake success, private object
mutation or replacement service is justified by this evidence.

## Preservation

Post-return verification passed: 115 prior EFI files unchanged, normal random
seed update and archived authorized removal of entry 051 accounted for;
firmware and four original commercial images unchanged; Ubuntu current/default,
original manual entry, unmounted lab partition and enabled/active screen-off
timer retained. Latest experiment entries are 052/053; shared payloads remain.
Archive manifest: reports/boot-entry-retention-20261114T153425277668Z/result.json.

Evidence under reports/commercial61-native-053: hwbreak-test.json,
overlay-result.json, boot-observation.json, post-return-verification.json,
hwbreak-analysis.json, render-analysis.json, runtime-analysis.json,
scanout-sample-*.ppm and runtime-evidence/retrieval-manifest.json.
