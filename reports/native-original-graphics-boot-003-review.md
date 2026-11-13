# Native original-service trial 003: root repair verified, next blocker exposed

## Physical result

Exactly one 003 trial ran on the MateBook and automatically returned to Ubuntu.
Target run: `native-original-003-86225b0f-8955-41c8-ba64-d42aa8cbac42`.
Ubuntu boot ID afterwards: `620c2f01-656b-43e2-993f-d181dfe2892e`.
All 39 collected snapshots retain their recorded SHA256 hashes.

`phase-039.log` confirms `NATIVE_ROOT_NAMESPACE003 rooted=1 chroot_fallback=0`.
Original init can stat its own `/data` in all three recorded samples (0–2),
including after service startup. This fixes the previously reproduced
namespace-root escape **within the observed window**, not a long-duration test.
The inner bootstrap is byte-identical to 002; no service identity, platform
runtime or EGL implementation changed for this repair.

## Genuine service progress, not desktop success

Sample 2 captures original `/system/bin/samgr` (PID 39), `param_watcher` (PID 40),
and `/system/bin/hdf_devmgr` (PID 63). The twelve matching library-map lines
are these processes' original platform `libc++.so` mappings, **not** evidence
that native Mesa or RenderService rendered anything. Samgr later reports
`JoinWorkThread error`; its observation does not establish service readiness.

The original init reports repeated `storage_manager` execution failures:
`[startup_failed]failed to execv 32 13 storage_manager`, followed by exit code 23
(raw wait status 5888). Errno 13 is EACCES. Hilogd and watchdog also show exec
failures; ueventd reports SIGSEGV. The fourth storage-manager failure triggers
the original critical-service panic/reboot path around 11.96 seconds. The
isolated namespace exits; outer sample 3 reaps it and safely ends the physical
diagnostic boot. Thus only three observer samples exist, not twelve.

The exact cause of this new execution-permission failure is **not yet proven**.
Next investigation must distinguish original file/interpreter permissions,
mount `noexec`, service sandbox mounts, and execution-time security behavior.
Do not bypass the critical-service check, forge readiness, relax unrelated
checks, or blame permissive SELinux AVCs as though they were enforcing denials.
RenderService, composer/allocator readiness, EGL output and desktop remain
unverified. Existing raw logs must not be rerun or overwritten.

## Preservation verified

- All three original images match their pre-boot SHA256 hashes.
- 79 static pre-existing EFI files are unchanged across boot; normal random
  seed rotation is recorded separately.
- Ubuntu remains the default, one-shot selection is cleared, and automatic
  screen-off remains active.
- LAB is restored read-only with noload, nosuid, nodev, noexec.
- Ubuntu's LSM remains `capability,landlock`. Target samples have SELinux
  enforcement 0; the initial policy-load audit is not retained in the final ring.

Evidence: `native-original-graphics-boot-003/runtime-result.json`,
`independent-verification.json`, and the immutable `native-logs` directory.
