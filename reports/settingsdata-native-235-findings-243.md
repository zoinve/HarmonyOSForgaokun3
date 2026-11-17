# Native235 Recovery Findings

## Acceptance

Settings UI remains unverified. Do not promote candidate197 over active165 or
boot candidate197 again before storage consistency is restored and checked.
USB work remains paused at181; working desktop173 is unchanged.

## Late Return

The original observation ended after its 21-minute budget without detecting
Ubuntu. Keep `commercial61-native-235/boot-observation.json` unchanged.
After the user reported restored connectivity,240 authenticated Ubuntu running
kernel7.1.0-rc3-gaokun3+ with a different boot ID. This proves a later Ubuntu
observation, not the cause of reboot or successful automatic fallback.

`commercial61-native-235/post-return-verification.json` verifies Ubuntu current
and default entries, enabled/active screen-off timer, unchanged firmware and
four original images. The only authorized removed entry is206; the random seed
is the other expected EFI change. The LAB partition was unmounted.

## Evidence Recovery

Standard retrieval stopped before export because the final desktop snapshot
was absent.240 retained physical-serial and original-UDID scans, using a
hash-verified prior privacy digest read through the compressed-history reader.
The whole-directory tar then failed on `phase-207.log` with EUCLEAN.

241 exported only the three readable, privacy-scanned, manifest-listed files.
All remote hashes matched locally. No raw tar was persisted. The manifest marks
the export incomplete and records the unreadable directory entry. Only one
readable cumulative phase remains; do not claim two or complete teardown logs.

## Runtime Change

`settingsdata-runtime-comparison-238.json` verifies all retrieved member hashes
for206 and235.206 had790 exact provider base-directory/sandbox failures;235 has
none of those exact failures in the recovered hilog.235 records four provider
stage creations, and the original hilog records `call initRdbStore end` after
initialization. This is real provider progress, not a Settings UI acceptance.

The four recorded Settings MainAbility-name references are SceneBoard icon
and icon-cache operations, not proof of a MainAbility launch or window.
No SceneBoard-watchdog reboot marker was found in the recovered235 hilog;
absence in incomplete evidence cannot prove full-run survival.

The readable phase records one strict namespace pin matching real target479,
but no target-exit/final-flush markers. Native teardown remains unproven.

## Storage

`commercial61-native-235/settings-data-offline-237.json` verifies active165
SHA256 unchanged, candidate197 marker matching235, and archived diagnostic
objects matching runtime. Read-only candidate fsck returns4; full native
storage acceptance is false. No repair was requested or performed.

`settings-storage-inspection-244.json` supersedes the locale-sensitive error
counts in242. Both layers were inspected read-only; the outer mount used
ro,noload. Outer LAB fsck reports two invalid extent ends, an inode block-count
mismatch, the dangling phase207 entry, an unattached inode and bitmap errors.
An independent read-only debugfs ncheck maps affected inode917545 to this run's
`interactive-hilog030.log`, not to active165. This does not prove other files
are safe from every possible metadata fault.

Inner candidate fsck reports an orphan-inode issue, two bitmap differences and
two free-count mismatches. Both layers have needs_recovery. A read-only check
skips journal replay, so these findings do not establish which inconsistencies
would remain after normal recovery. Do not assert a kernel bug or user-forced
reboot as the cause without further evidence.

Candidate postboot SHA256 is
`628bbf9d1902e19fba205348917925483543eb71fdbd2ecf95406a57a8e7918a`.
Active165 remains
`36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce`.
All inspection mounts were removed. No extra full-size disk clone, new boot,
identity injection, security bypass or Settings launch request was made.

## Verification And Next Work

Three runtime-parser tests passed. Five new/updated scripts and generated241
retrieval parsed successfully; manifest-only tar selection, both privacy scans
and non-persistence of original.tar were checked directly.

Determine whether the return was manual or automatic; preserve that uncertainty
until answered. Before any writable recovery, preserve verified compact
metadata/rollback evidence outside LAB, protect active165 and original images,
and identify the least invasive journal/filesystem recovery procedure. Recheck
outer and inner filesystems and active165 bytes afterward. Only then resume a
single bounded Settings UI acceptance run with reliable terminal evidence.
