# Native 063: Original Account Lifecycle Retry

## Result

The authentic desktop is not verified. All seven 160x256 sparse scanout samples
remain black. Do not repeat operational boot 063.

The single init-managed account-service retry after genuine WMS readiness
succeeded. Original accountmgr PID 4094 activated original account 100:
OnStartUserDone returned 0 at guest 50.114 seconds; the original service wrote
bootevent.account.ready at 50.135 seconds. The bounded script independently
read its actual value as true. No caller token, UID or boot flag was forged.
The first activation at 47.310 seconds had returned 22 and rolled back.

This resolves the observed account activation ordering failure, not the entire
boot lifecycle. BootAnimationNode still rendered at 120.015 seconds; no observed
whole-system completion or node-release evidence establishes cleanup. Original
init static disassembly shows a separate event counter gates its own completion
write. Missing external setter logs cannot enumerate all internal event writes.

SceneBoard first flush was 103.665 seconds. Two subsequent composer frames were
observed, ending at 120.056474 seconds, with no sampled nonblack frame. Hardware
observation had 196 attachments, zero attachment failures, lost samples,
malformed records or instruction-pointer mismatches; 3569 sample log lines were
suppressed, which is not perf-ring loss.

## Preservation

Run: commercial61-native-063-76551421-7d9a-4d47-aabe-49ad59fd0e8a.
Single operational boot: 2026-11-14 18:10:44Z to 18:14:25Z.
Returned Ubuntu boot: b459a481-501f-4aa4-9051-9483219510d0.
All 64 retrieved files matched remote hashes; retrieval did not replay the
original partition. The full return verifier passed: Ubuntu current/default,
firmware and four images unchanged, original manual entry retained, lab partition
unmounted, screen-off timer enabled/active. The only boot-managed EFI change was
random-seed; removal of archived entry 061 was user-authorized. Latest experiment
entries are 062 and 063.

## Evidence And Next Work

See commercial61-native-063/account-analysis.json, account-script063.log,
and the hardware, render and minimal analyzer outputs in that report directory.
The raw log explicitly reports unsuccessful writes of hdf_devmgr.ready and
composer_host.ready with result 1001. These failures alone do not prove either
event is still blocking completion. Reconcile original image declarations and
ACLs with actual original init aggregation before choosing experiment 064.
Retain the verified 063 account lifecycle repair in future candidates.

## Read-Only Follow-Up

commercial-event-declarations-063/result.json records 46 matching original-image
files, their hashes, 12 service declarations and the observed external event
writes. The chipprod /etc/init/hdf_devhost.cfg explicitly declares
bootevent.composer_host.ready for the original composer_host service, with its
original composer_host UID. The scanned top-level parameter files contain no
dedicated ACL for this event or hdf_devmgr.ready; system ohos.para.dac has the
root-owned bootevent. prefix. This is a candidate configuration mismatch, not
proof of the exact error-code meaning, effective loaded ACL or remaining count.
The scan does not establish recursive configuration/import coverage or actual
runtime event registration. Do not weaken permissions based on this alone.

All three reference source trees were searched for these two event names and
whole-system completion handling in relevant scripts/configuration/source.
No specific fix was found. HarmonyMac's native-desktop-start.sh force-stops
startupguide after normal aa startup; that step remains unadopted. The L410
graphics integration and HarmonyMac queue/composer integration remain useful,
while Linux Compatibility Platform supplies post-desktop application support.

The next bounded experiment should retain 063's successful account ordering and
read actual event values and original init processing evidence. It must not
write completion flags, impersonate service identities, or forcibly terminate
the boot animation to manufacture a visible result.

## Audit Correction

The initial follow-up used the wrong vendor filesystem root. Its empty vendor
listing must not support an absence claim: this image has /etc directly at its
root, not /vendor/etc. Read-only inspection found the original files
/etc/param/composer_host.para.dac and /etc/param/hdf_devmgr.para.dac. They assign
each ready parameter to its matching original service account with mode 0775.
The incomplete first audit remains preserved; use the corrected
commercial-event-declarations-063-r2 scan for vendor declarations and ACLs.
Investigate loading/effective rules rather than creating new permission grants.
