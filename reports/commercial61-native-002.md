# Commercial image: minimal startup adjustment 002

## Scope and result

The only functional adaptation after 001 is creating the volatile directory `/data/local/tmp/l410-vulkan-r18`, mode `0750`, owned by the original RenderService account `1003:1000`. Its original launcher redirects output there before executing RenderService; the directory was absent from the fresh RAM data filesystem.

The original commercial init, service configurations, launch scripts, shared libraries and credentials remain unchanged. There is no SDK userland substitution, injected input or bypass of a failed service. The original four commercial image hashes were rechecked at installation; all are mounted read-only. No installer or partition-formatting program is executed.

The single 002 operational test ran on 2026-11-13 from 08:04:11 UTC to 08:09:34 UTC and automatically returned to Ubuntu. Original `/system/bin/render_service`, absent in 001 samples, is now observed repeatedly with the same inner PID 746. This demonstrates successful execution after repairing the launcher's required directory, **not** a healthy renderer or a working desktop. The HDF service-manager startup failure remains unestablished.

## Evidence and limitations

- The 67 captured files were retrieved with matching remote/local hashes using an original-partition `ro,noload,nodev,nosuid,noexec` mount, then unmounted. No journal replay or filesystem repair was performed.
- The inherited capture helper intentionally closes descriptors 198 and 199 before init. The additional 002 diagnostic helpers mistakenly wrote to the already-closed 199. Early kernel and redirected renderer logs are therefore incomplete; missing messages must not be treated as evidence of success or absence of errors.
- 003 fixes only diagnostic descriptor ownership: a private close-on-exec duplicate is retained for passive children and closed before original init executes. A real fork/exec regression test first reproduced the missing output against 002 and then passed against 003. No extra service adaptation is bundled with that correction.
- Ubuntu is the default after return, boot ID `f0157e76-3511-4229-a389-9497f5541945`. The user-disabled screen-off experiment timer remains disabled. The existing manual GPU entry remains retained.
- Independent 003 testing is recorded separately; completed 001/002 trials and artifacts must not be overwritten or rerun.

See `commercial61-native-002/minimal-startup-analysis.json` and `commercial61-native-002/runtime-evidence/` for bounded process observations and original evidence. The specified ISO identifies its commercial userland as `6.0.0.110 API 20`; this is not relabelled as SDK 7 or a different release.
