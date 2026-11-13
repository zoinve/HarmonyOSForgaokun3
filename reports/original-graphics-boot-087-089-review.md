# Original SAMGR path observation 087; canonical mount candidate 089

## Verified 087 evidence

Experiment 087, its disposable-data recovery, and its independent verifier each
ran once. See `original-graphics-boot-087-independent.json` and
`original-audit-copy-087/result.json`. No VM was rerun for recovery.

The receiver copied genuine audit multicast messages without replacing the audit
receiver. The kernel accepted the UID5555 logging-only rule. The recovered log
contains 2,889,422 bytes, SHA-256
`d2e63c7955a3b53114177cdd806b39bc5ba2ee4a1e5236a25b13e28ec1ca8014`.
Its collector reported 20,105 records and **13,687 dropped notifications**;
this is incomplete evidence, not proof that unobserved accesses never occurred.

Four complete audit events `26.476:1045` through `:1048` identify genuine SAMGR
PID135, original UID5555/domain `u:r:samgr:s0`, AArch64 `faccessat` syscall48,
and return **-2 / ENOENT**. Same-serial PATH records identify:

- `/usr/system/profile`
- `/usr/system/variant/pc/base/profile`
- `/usr/system/variant/pc/china/profile`
- `/sys_prod/profile`

These are actual early SAMGR results, unlike the separate UID0 configuration
query. They do not establish why the paths were unavailable, nor imply EACCES.
Expected unsuccessful dynamic-loader search probes are not classified as fatal.

Recovery repaired only a newly created clone of disposable guest userdata.
Original retained scratch hash remained
`0b5f0343fa20c312f3fe6a01d30157e12886941f5c7321361dc5fcc917e7d2ad`.
The independent verifier checked all 12 graphics provider files, ashmem/query
helper, archive/kernel, all three original SDK images, and 378 prior native logs.
No desktop or physical display success is claimed.

## Hypothesis and safety gate

The original custody configuration starts with `/system`; the bootstrap used a
symlink from `/system` to `/usr/system`. Candidate 088 changes only this layout to
a read-only bind of the **same original files**. Its build completed, but review
found that the bind remount omitted the source image's NODEV flag. **088 was not
booted.** Its completed build and evidence remain intact, not overwritten.

Fresh candidate 089 explicitly preserves `MS_RDONLY | MS_NODEV` on that bind.
The source image stays read-only; existing volatile provider overlays remain the
same. Original profile contents/priorities, credentials, policy, databases,
providers, and kernel are unchanged. SELinux remains permissive, not disabled.
This is a path-layout hypothesis, not a claimed SA511 or BMS fix.

## 089 preparation and pending execution

- Explicit offline suite: `test-original-system-bind-088.py`, 3 tests passed
  after the new NODEV-preservation case first failed for missing 089 fixture.
- New runner/recovery/verifier sources generated and compiled offline only.
- Preparation ran once successfully. Init: 854,728 bytes, SHA-256
  `ac5c9f01d95869574d923f9d7af09e69676d94a19ea5f7cadfaa0e860717fcdc`.
- Policy and graphics-init configuration match the prior pinned hashes.
- Fresh isolated 089 VM is running at the time of this record: 480-second bound,
  TCG, virtual display, read-only SDK images, disposable RAM-backed data, no guest
  network or host shares. No MateBook/Ubuntu operations were performed.

After automatic completion, recover 089's audit copy from a new disposable-data
clone **before** running its independent verifier. Inspect actual profile-access
returns, genuine SA511/BMS/desktop responses and QMP pixels; do not infer business
success from a CLI exit status or from the mount hypothesis alone.
