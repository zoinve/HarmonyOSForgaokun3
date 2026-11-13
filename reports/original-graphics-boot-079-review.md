# Original desktop request diagnosis 079

## Verified outcome

The corrected original `hilog -z 200 -P <foundation-pid>` requests completed
without the incompatible-command error from 078. Actual Foundation/BMS logs
show repeated ENOENT opening
`/data/service/el1/public/bms/bundle_manager_service/bmsdb.db`, missing parent
directories and a null RDB store. This is business failure evidence, not a
successful installation or desktop start. Other authentic extension-privilege,
signature/HAP and missing-syscap errors remain separate unresolved failures;
none of those checks were relaxed.

Evidence: `reports/original-graphics-boot-079-independent.json` and the original
serial/results in `reports/baremetal-sdk-original-init-qemu-079/`. The verifier
ran once successfully, checking the injected graphics files, actual ashmem
module, archive/kernel, all three full original SDK images and all 378 prior
native raw files. No physical desktop, fresh host screen check or successful
HarmonyOS desktop is claimed. All runtime work remained in the isolated WSL
VM; Ubuntu and the MateBook were not modified.

## Read-only root-cause investigation

`reports/original-userdata-jobs-001/result.json` records a read-only audit of
194 original system/vendor init configuration files. Existing Foundation jobs
create the legacy `database/bundle_manager_service` path, not the new `bms`
path. That difference alone does not authorize a replacement mkdir job.

The genuine BMS library was independently extracted and hash-pinned:
`36fcf01ce7079acf0ba68aa2e08368fb3aaba418325be6d6f6b62988aa903627`.
See `reports/original-bms-paths-001/` and
`reports/original-bms-startup-001/`. Read-only original disassembly establishes
that `BundleMgrService::CreateBmsServiceDir` delegates the exact new directory
to the original `InstalldClient::Mkdir`, requesting mode 0755, UID 5523 and GID
1000. A second request creates its `app_install/` subdirectory, mode 0771,
UID 5523/GID 2002. The original client obtains/loads the authentic on-demand
installs service. Neither the actual runtime proxy failure nor the mkdir
return code is established by static analysis.

No database was fabricated, directories manually injected, signatures bypassed
or original service identities changed. The completed audits and experiments
were not rerun or overwritten.

## Next experiment

080 retains the same original services and graphics stack. It selects the
first 600 original Foundation log records rather than the late tail, aiming
to capture the authentic installs activation/directory-creation failure.
At this report's writing it is running; no result is assumed. Original bm/aa
requests and their actual failures, read-only SDK disks, permissive guest policy
and independent scanout-image checks remain intact.
