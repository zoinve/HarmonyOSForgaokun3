# Persistent data backup and offline recovery, November 16, 2026

No native boot was performed in these operations. Completed boot 168 remains
immutable and must not be rerun. Overall hardware integration remains active.

## Verified Backup

`persistent-data-backup-169/result.json` records an inactive, read-only,
no-journal-replay copy of the 8,589,934,592-byte data image. The local compressed
archive is excluded from Git, contains the filesystem rather than exported
application-file logs, and must be retained for rollback.

- Source SHA256: `9ea5a6ce673b90ccce079d418bf136eccb2f7dff4597b2295b930a86b0f84828`.
- Compressed bytes: 1,770,116,849.
- Compressed SHA256: `5f190884ce44166a24f8919c89e9663cdc2457002b7188ffe1d2e6872716fcd0`.
- Full decompressed byte count and hash match the source.

## Separate Recovery Trials

Trial 169 used a verified local copy. Automatic `e2fsck -f -p` refused the
orphan-list inconsistency, returning 4; the subsequent read-only check also
returned 4. That copy and all failure evidence remain intact. A failed preen
must not be interpreted as necessarily byte-preserving on its trial copy.

Trial 170 independently decompressed the original verified backup into another
local copy. Full `e2fsck -f -y` returned 1 (corrected errors), followed by
`e2fsck -f -n` returning 0. File and allocated-block counts remained 17,301 and
856,986 respectively. The compressed backup remained hash-identical.

The outer LAB filesystem was checked separately while unmounted, using only
`e2fsck -f -n`; it returned 0. Its header retains historical error records,
first November 12 and last November 15, with `ext4_lookup`/EFSBADCRC. Its
mount warning is already present in boot 164, before persistent data. No outer
filesystem repair or error-flag clearing was performed. A clean present check
does not establish the cause or resolution of those historical errors.

## Source Repair 171

After revalidating the compressed backup, successful trial and outer check,
the source was mounted read-only and fully rehashed. It matched the backup
source hash exactly; the 110 observed orphan inode numbers matched the trial.
Only then was LAB mounted writable for an offline repair of the inactive
`harmony-persistent-data-165/data.ext4` regular file, with exclusive locking,
inode/capacity checks and no active loop mapping.

Repair returned 1, and the subsequent forced read-only consistency check
returned 0. The filesystem header is clean, the expected inner UUID and native
boot marker `4294d07e-b415-4edb-b707-cd05bde7fa49` remain, and the SceneBoard
installed directory remains present. File and allocated-block counts are
unchanged. No application database was reset, no seed was copied, and no
original system image was a repair target. LAB was flushed and unmounted.

Source SHA256 after repair:
`e6a8c83be01dfe8668127d29312bf635246bcd57bf5b497a697e3d2791f27923`.
Authoritative evidence: `persistent-source-recovery-171/result.json` and its
transport outputs, plus the independent numbered trial and backup reports.

## Remaining Work

Offline recovery is verified; prevention of recurrence is not. Runtime flush
success from 168 is insufficient proof of graceful service shutdown or release
of all mount references. Inspect and correct that lifecycle before declaring
persistent storage stable. Warm-start desktop readiness also remains unresolved:
168 never observed the SceneBoard process. Account-start error 22 appears in
the older 164 baseline too, so it is not by itself a differential root cause.

Do not return to OOBE/activation experiments, delete application databases,
bypass signatures/authentication or replace the known desktop seed. Resume
touchscreen/USB service and physical-workflow verification on a restored usable
desktop, preserving Ubuntu default and numbered evidence.
