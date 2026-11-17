# Commercial 052 closure

The sole boot ran 2026-11-14T15:17:39.774230Z through
2026-11-14T15:21:21.991404Z, returning to Ubuntu boot
018abb4e-d602-4e19-a1f1-f6739d7b1abf. Do not repeat 052.
All 64 raw files match remote hashes after ro,noload retrieval. No journal
replay was performed. Normal target timeout, target exit status 9, and observer
shutdown before cleanup are recorded in phase-062.log.

## Verified observer correction

The 052 resolver does not equate OverlayFS stat identity with proc maps.
It checks the audited entry instruction, exact original library path and an
executable, readable, nonwritable mapping; opens the actual service's proc mem
read-only; compares the entire executable mapped interval against the original
ELF file bytes; and rechecks the exact mapping record before resolving an
address. It writes no target memory or instructions. Short reads, differences,
invalid ranges and mapping changes fail closed.

Offline tests passed for multiple comparison blocks, nonzero file offsets,
single-byte changes at both ends and block boundaries, invalid/short reads,
range overflow and changed mapping permissions. Perf ring wrap, register layout,
lost-record and partial-header fixtures also passed. Full 052 differs from
full 045 only in init. Bootstrap, modules and original userland are unchanged;
the incremental ordered archive chain equals full 052.

Runtime resolution succeeded for all four audited addresses on original RS
global PID 1228. There are 208 successful event attachments and zero logged
attachment/mapping failures. Actual sample records: request 251, recv_parcel 16,
on_vsync 248; register_agent zero. No lost, malformed, suppressed or IP-mismatch
records were reported. This establishes actual hardware-breakpoint sampling on
kernel 045, not complete call coverage: attachment occurs on periodic scans,
new threads may execute before being scanned, and zero records for a function
do not prove that it never ran.

## Desktop evidence and next boundary

Original SceneBoard PID 3829 installed and ran; missing-application-agent
warnings are absent. First ArkUI flush is at guest 89.318 seconds; last
Composer frame is at 81.433420 seconds. Zero post-flush frames were observed.
All seven exported 160x256 scanout PPM images contain only black pixels.
Native desktop pixels and interaction remain unverified.

Of the actual samples, 15 RecvParcel caller arguments are authentic SceneBoard
PID 3829 and one is startup-guide PID 4357. All captured RecvParcel x2 and x6
values are zero. After SceneBoard's first flush there are 4 RecvParcel entries,
13 RSMainThread::OnVsync entries and 46 OnRemoteRequest entries. After the last
Composer frame there are 12, 117 and 87 respectively. These counts use perf
CLOCK_MONOTONIC timestamps and the existing UI/frame time correlation.

Thus transaction entry and main-thread VSync activity exist while no new
Composer frames arrive. Entry samples do not prove successful unmarshalling,
transaction processing or rendering. The next justified observation boundary
is unmarshalling and RS transaction processing, using already audited offsets
and the working 052 resolver. Do not replace original RS/SceneBoard or treat
client flush return as proof of service processing. Preserve the three-reference
full graphics route and focus tests on the actual service integration failure.

The prior 051 display power status 0 must not be interpreted as proof of
screen-off: reference DisplayComposerType.idl defines POWER_STATUS_ON=0, and
the HarmonyMac stock RS scene probe requests power 0. Distinct power domains
and APIs require version-matched interpretation.

## Preservation

Post-return verification passed: 114 prior EFI files unchanged, normal random
seed update and authorized archived entry 050 removal accounted for; firmware
and all four original commercial images unchanged; Ubuntu current/default,
original manual entry, unmounted lab partition and enabled/active screen-off
timer retained. Latest experiment entries are 051/052; shared payloads remain.
Entry archive: reports/boot-entry-retention-20261114T151723463452Z/result.json.

Evidence under reports/commercial61-native-052: hwbreak-test.json,
overlay-result.json, boot-observation.json, post-return-verification.json,
hwbreak-analysis.json, render-analysis.json, runtime-analysis.json,
scanout-sample-*.ppm and runtime-evidence/retrieval-manifest.json.
