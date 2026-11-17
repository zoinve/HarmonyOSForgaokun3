# Commercial native 008 — manual recovery, no working desktop

The user reported **“卡死手动重启”**. This run is recorded as manual recovery, not successful automatic return. The runner's historical `returned: true` only establishes Ubuntu became reachable and is preserved unchanged.

## Scope and outcome

008 adds only `/usr/system -> /system` inside the original system/chipset service sandboxes, where the relevant `/system` subdirectories were already exposed. All original mount grants, service credentials, capability and signature checks remain unchanged. The commercial images are used read-only; no SDK userland was substituted.

The original samgr now discovers `/usr/system/profile`; the original `installs` service executes `installd OnStart`. The previous SA 511 “not supported” error is absent in this capture. **SceneBoard installation returns `resultCode: 0` at 08:00:36.948. This is installation success, not a running desktop.** Earlier capability-list warnings must not be misreported as the final installation result or bypassed.

At approximately 08:00:41.714 the original installer cannot create application directories under `/data` (`errno:28`); SQLite subsequently reports full storage (`Error[13], sys[28]`). The temporary 3 GiB guest data filesystem is insufficient for this commercial first-boot workload. Host Ubuntu disk usage is a separate issue. No storage-size modification or new boot has been performed following the user's report.

The original RenderService still attempts the supplied L410/Mali backend and reports failure creating the kernel-driver context. A compatible FD690 backend remains necessary. No SceneBoard process or displayed desktop has been verified.

## Freeze and exit evidence

The captured parent log records `target_budget_seconds=90`, `COMMERCIAL008 target_timeout=1`, target exit status 9, and `NATIVE_ORIGINAL_END`. Thus the diagnostic target was deliberately terminated at its configured timeout. These records **do not establish that the host completed an automatic reboot** or identify the precise cause of the user's perceived freeze. No kernel-deadlock conclusion is warranted from this capture. The user's manual reboot is authoritative.

Further operational boots have been paused. Investigate the complete host teardown/reboot path, guest storage sizing and real graphics integration offline before another test; do not repeat 008.

## Preservation

- Run: `commercial61-native-008-9213b088-db8e-4d7d-823a-eb4220b4a665`.
- 59 files retrieved using read-only `ro,noload,nodev,nosuid,noexec` access to the evidence partition, hashes matched and the partition was unmounted. No journal replay or filesystem repair was performed on the original.
- Latest snapshot: `phase-057.log`; authoritative original streams retain their historical `030` filenames.
- Ubuntu returned with boot ID `7adefc99-99dd-4571-a9b0-bba67c1ca0fc`. Ubuntu remains the default; the custom forced-screen-off timer remains disabled.
- Analysis: `commercial61-native-008/manual-recovery-analysis.json`; selected evidence: `manual-recovery-evidence.txt`. Original runner results, images, earlier numbered evidence and the manual GPU entry are retained.

An independent commercial-runtime hardware link test was started offline before the manual-reboot report: only its failing test and read-only runtime-library audit exist. There is no completed 009 build, deployment or runtime result.
