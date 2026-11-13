# Native presentation 043 — deployment and single-boot gates

## Completed before runtime

- The separately built/audited 043 overlay is 345,590 bytes, SHA-256 `b2a0581f8869ca1d5fb6ee62bd1d0b1866c32832c73d811411f53a6f076fa3f7`. Its two members are the new run-labelled init and the instrumented original composer VDI. Other services, images, identities, renderer logic, cursor behavior and input remain unchanged.
- Inert device staging verified all ten files and actual ARM64 non-PID1 refusals. No old operational experiment was replayed.
- The already-consumed 022 entry and its exclusively referenced image were copied, fsynced and hash-verified in `native-original-graphics-boot-043/efi-archive-consumed-022` **before** removing only those EFI source copies. All remaining 102 EFI files were unchanged; no runtime evidence was touched.
- First installer 043 refused a list/map metadata mismatch before creating a journal or EFI file. That failure is preserved. Fresh attempt 002 normalized the genuine nine artifact rows, passed its tests and installed only `native-original-graphics-043+1.conf` and the new overlay. Existing 102 files, firmware, Ubuntu default and screen-off timer were preserved. ESP free space after installation: **70,909,952 bytes**, above the **64 MiB** reserve. No one-shot or reboot was requested by installation.

## Fresh executor and evidence checks

- `run-native-presentation-043.py` rechecks actual Ubuntu boot ID, ESP identity, firmware, all installed EFI hashes/configs, candidate/staged hashes, free reserve, boot count, no pending one-shot and enabled/active screen-off timer. It creates an exclusive, fsynced nonce-bound journal, selects only its counted entry and issues **one** reboot request.
- Reconnection begins immediately, with no initial sleep; only a changed boot ID running Ubuntu is accepted. Observation is bounded to 720 seconds (individual SSH probes up to eight seconds). No second reboot is attempted. Pre-reboot failures can clear only the same nonce's own pending selection; no unrelated/default entry is changed.
- Target budget remains 240 seconds, independent outer fallback 420 seconds, panic timeout 15. These are software safeguards, **not** proof of recovery from a hard kernel wedge. No hardware watchdog guarantee or synthetic input is introduced.
- Collector requires the exact lab UUID/PARTUUID, mounts read-only with `noload,nodev,nosuid,noexec`, accepts one uniquely numbered run, verifies every regular file and unmounts. Bounds: 512 files, 64 MiB per file, 512 MiB total. The local tar reader rejects traversal, links, duplicate or mismatched members. Existing 041 evidence totaled about 174 MB; bounds allow the additional capped telemetry without becoming unbounded.
- Independent return verification preserves the fresh `loader/random-seed`, checks the consumed counted-entry rename, unchanged other EFI bytes/default/firmware, read-only lab collection, logical screen-off **without invoking a setter**, all 71 prior 041 and 378 older native raw hashes, and three full original SDK images. Actual callback analysis keeps cursor updates separate from client frames. Submission IDs are not visual-content identities, initial modesets are excluded, and bounded/unflushed tails remain unknown.

Offline gates: executor/collector/return checks **5 passed**, deployment checks **5 passed**, analyzer checks **3 passed**. The actual boot, returned evidence, completed presentation counts and any FPS interpretation remain **pending** at this report's creation. No touchpad/click/status-bar or stable 120 FPS claim is made.
