# Settings investigation through 214

USB work remains preserved at 181 and is not resumed. Working desktop 173 and
active data 165 are not replaced. Settings UI acceptance remains incomplete.

## Confirmed directory defect

The immutable source/target reports under settingsdata-directories-214 compare
original installer directory metadata against isolated candidate 197 after 206.
The original installer contains app/el1/0/base/com.ohos.settingsdata, owned by
20027:20027 with mode 0700, and its .backup, haps, haps/entry and preferences
directories. All six of these directories are absent from the candidate.
Existing SettingsData database directories do not replace the missing base tree.
Missing aot_compiler/log paths without a matching original source entry are not
independently classified as defects.

206 original service logs show ENOENT for that base directory, followed by
SettingsData appspawn sandbox bind failure (218103816). SceneBoard's original
THREAD_BLOCK_6S stack waits in DataShareConnection and libsettings while its
SystemUISettingsManager initializes. Repeated SceneBoard exits trigger the
original reboot protection. This is a concrete provider failure chain, but not
proof that repairing this directory alone will resolve every Settings UI issue.

## Misleading CLI error

The single root aa request in 206 returned textual error 10103601. Matching AMS
logs reject the actual caller for missing START_ABILITIES_FROM_BACKGROUND;
therefore this message does not prove that the Settings bundle is absent.
Read-only BMS/token audit 208 confirms enabled Settings MainAbility for user 100.
Original Settings background extension activity is not a verified MainAbility
window. No caller-token injection or permission bypass was performed.

## Preservation and limits

214 target inspection used read-only/noload and left candidate SHA256 unchanged:
c62688255719b2b36018f10da02d9d7413f55b0d1c8108a82d5e5b0d6e605b42.
The LAB partition was unmounted afterward. 212 reports fsck clean, but 206 native
teardown failed after early target death; offline cleanliness does not establish
successful native flushing.

213 confirms original system/vendor/sysprod/chipprod images and 188 prior EFI
files unchanged, Ubuntu current/default, and screen-off timer enabled/active.
Firmware text is NOT unchanged: the USB boot option disappeared and BootOrder
changed from 0001,0000 to 0001. Cause is not established by this comparison.
The original working data165 hash remains recorded as unchanged in 212.

## Repair boundary

Prepare a new isolated revision containing only missing empty scaffolding with
original source-derived ownership, modes and verified policy labels. Preserve
existing databases, genuine bundle/token records and working data165. Do not
copy account/activation state, disable sandbox checks or suppress the SceneBoard
watchdog. Verify a genuine UI launch and post-return preservation before any
promotion. No new boot or filesystem repair was performed by audit 214.
