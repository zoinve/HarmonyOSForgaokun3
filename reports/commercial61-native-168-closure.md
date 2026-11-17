# Persistent native boot 168: retained data, desktop and consistency gaps

One completed bounded boot, not to be repeated:
`commercial61-native-087-4294d07e-b415-4edb-b707-cd05bde7fa49`.
Started November 16, 2026 at 07:43:39 UTC; Ubuntu return observed at 07:47:21 UTC.
All 182 retrieved evidence files match their remote hashes.

## Verified Progress

- The same NVMe-backed 8 GiB data filesystem was mounted read/write by the
  original runtime. Previous boot marker `61950145-5809-4403-9c56-c820c3390a07`
  was retained; no seed reset occurred.
- The additional archive of `commercial-memmgr108.log` succeeded. Original init
  handoff occurred, removing the specific pre-init EEXIST failure from 167.
- Inner syncfs/unmount and backing fsync/outer syncfs returned success. These
  syscall results alone are not filesystem consistency or graceful shutdown proof.
- The authenticated native read-only diagnostic channel connected at
  192.168.10.247, observed growing logs, rejected an arbitrary shell and reaped
  its helper. Original MMI holds the touchscreen; storage modules are live.

## Incomplete Acceptance

The original SceneBoard process was not observed in any recorded process sample.
The existing-SceneBoard guard failed, as on 166. BMS restored retained application
metadata, but no SceneBoard installation was scheduled in this boot. There were
five valid nonblack composer frames, last at monotonic 25.909274 seconds, not
evidence of a usable desktop. Do not treat this as desktop or physical-input
acceptance. The original user-confirmed desktop baseline remains separate.

The offline verifier failed at its read-only e2fsck gate. An independent read-only
inspection preserved the full diagnostic in
`commercial61-native-168/persistent-fsck-inspection.json`: e2fsck exit 4,
orphan-list/inode errors. The header reports clean, but the stronger consistency
check fails. No repair, formatting, seed replacement or application-data reset
was performed. LAB was unmounted after inspection.

`persistent-runtime-analysis.json` verifies runtime mount/identity/flush only;
its true runtime result must not be interpreted as full storage acceptance in
the presence of this failed offline check. Application settings persistence was
not independently tested.

## Preservation And Next Work

Post-return verification passed: Ubuntu current/default, no pending one-shot,
screen-off timer enabled/active, firmware and all four original images unchanged,
182 prior EFI files unchanged. Normal random-seed changes and the archived,
user-authorized removal of the 166 entry are accounted for. Retained experimental
entries are 167/168; shared payloads and original manual entry remain.

Before another writable persistent boot, preserve a verified backup of the
current data file and investigate namespace/process teardown and orphan recovery.
Do not repair the only copy or infer that a remount proves the original service
mounts and open references have all gone away. Investigate warm-start SceneBoard
readiness from original service logs without another OOBE/activation experiment,
identity changes, signature bypasses or deleting application databases.

The basic-driver goal remains active, with touchscreen and USB prioritized.
