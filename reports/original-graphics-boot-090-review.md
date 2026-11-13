# Original graph 090: account startup and disposable-data capacity

## Verified 090 result

- Original accountmgr PID1407 was queried by the original HiLog tool at samples
  24, 30 and 41; all three queries exited zero. This is query completion, not
  successful account creation or desktop readiness.
- Actual account creation for user100 failed: BMS replied8521220, followed by
  `OS account 100 not created completely`. The meaning of8521220 remains unmapped.
- Subsequent original account storage checks reported insufficient storage with
  freeBytes10911744,10498048,10444800 and10428416, despite small requested writes.
  Actual logs then report failure to insert account100, code4194346.
- These are genuine failures in the fresh512MiB test volume. No account files,
  database contents, identities, permissions or success replies were fabricated.
  Increasing capacity is a hypothesis for this observed storage failure, not a
  claim that all BMS, bundle-validation or desktop failures share that cause.

Independent evidence: `reports/original-graphics-boot-090-independent.json`.
Serial SHA-256:
`f264391a81ac9b7bd91f036efc7d14a71150cf1f47c604334320002d32ca7d3a`.
The independent checks retain all12 injected provider ELFs, real ashmem module,
configuration-query helper, initrd, kernel, three full original SDK images,
previous378 native raw files, original identity/mode and PPM/PNG pixel checks.
No Foundation critical fault or guest reboot was observed within the bound;
desktop and physical-board verification remain false. No fresh Ubuntu-host or
physical-screen check is claimed: all work here ran inside WSL's isolated VM.

## Fresh 091 experiment, pending

- Keep the verified canonical `/system` read-only NODEV bind, original services,
  credentials, SELinux permissive policy, profiles and graphics providers.
- Replace only this new guest's disposable512MiB data image with an8GiB sparse
  file in the private WSL experiment directory. This is disk-backed, not RAM-backed
  and not an attached host device or original userdata partition.
- Require17GiB free space before allocation; stream hashes and retain a verified
  sparse evidence copy. Remove only this run's exclusive temporary file.
- Record actual `/data` statvfs capacity at account query samples. The independent
  verifier additionally rehashes the8GiB retained file; failed statvfs reads are
  represented as unknown rather than zero free space.
- Retain the480s observation bound, QMP screenshots and real original bm/aa
  business responses. No account, package-signature, activation or storage guard
  is bypassed. Original services must create their own real data.

Preparation091 succeeded once: init853768 bytes, SHA-256
`add781db526011e338945affbeac56f00a44952223f8ecdc525696a271b2b808`.
Original policy and graphics-init config hashes remain unchanged. Explicit offline
capacity tests passed3/3, including independent-volume and failed-statvfs cases.
Runtime091 is pending; no capacity fix, account success or desktop is claimed.
Completed090 and preparation091 must not be rerun or their evidence overwritten.
