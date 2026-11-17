# Commercial 051 closure

The single boot ran 2026-11-14T15:03:20.003069Z through
2026-11-14T15:07:02.113526Z, returning to Ubuntu boot
d318721b-6c0f-4ccb-a299-bf7a19f8109b. Do not repeat 051.
All 83 raw files matched remote hashes after ro,noload retrieval; the original
partition journal was not replayed. Normal target timeout, target exit status 9
and observer shutdown before cleanup are recorded in phase-081.log.

Offline tests passed for wrapped perf records, full-file equality with different
inodes, and rejection of a changed byte. The full archive differs from 045 only
in outer init; original bootstrap, userland and modules are unchanged. The
incremental ordered archive chain equals the full 051 archive.

SceneBoard runs without missing-application-agent warnings. First ArkUI flush
is at guest 72.353 seconds; last composer frame is at 70.833526 seconds. There
are no observed post-flush frames or sampled post-flush nonblack frames.
Native desktop pixels and interaction remain unverified.

The observer found original RS global PID 1231 but attached zero hardware
events and obtained zero samples. Twenty map candidates were rejected before
perf_event_open. For the request library, candidate diagnostics show root-path
inode 267527, device 0:22, versus maps inode 267527, device 0:20. map_files opened
successfully but its identity gate rejected it. Actual map_files fstat values
were not logged. Full-byte comparison was short-circuited by that gate, so the
log field full_bytes_equal=0 does NOT establish differing file contents.

Exact kernel 045 source explains why the map_files strategy is insufficient:
fs/proc/base.c:2282 assigns file_user_path(vma->vm_file) to the returned path.
fs/backing-file.c preserves a separate user path for stacked files while mmap
uses a real backing file. Opening map_files is therefore not a guarantee that
fstat exposes the device/inode printed in maps. Do not simply remove identity
checks or claim unsupported hardware breakpoints. Next address validation must
prove the actual executable mapping, for example by read-only comparison of its
executable bytes against the audited original ELF, with explicit failure paths
and offline mismatch tests. No new runtime validation method was deployed here.

The initial Windows Python installation attempt failed locally before SSH
because the existing transport adapter expects WSL. The WSL installation then
completed once; no diagnostic boot was duplicated.

Post-return verification passed: 113 prior EFI files unchanged, normal random
seed update and authorized archived entry 049 removal accounted for; firmware
and four original commercial images unchanged; Ubuntu current/default, original
manual entry, unmounted lab partition and enabled/active screen-off timer
retained. Latest experimental entries are 050/051; shared payloads remain.

Evidence: reports/commercial61-native-051/{boot-observation.json,
hwbreak-test.json,overlay-result.json,hwbreak-analysis.json,render-analysis.json,
runtime-evidence/retrieval-manifest.json}; boot entry archive manifest is
reports/boot-entry-retention-20261114T150258895560Z/result.json.
