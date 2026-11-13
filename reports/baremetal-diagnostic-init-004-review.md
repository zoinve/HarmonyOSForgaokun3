# Diagnostic init 004 — offline budget revision

## Scope and change

Preparation only: no candidate kernel boot, EFI entry installation, reboot,
host module loading, HarmonyOS launch, identity-policy patch or watchdog change.
001–003 sources and archives remain immutable.

The generated 004 source admits work against one `CLOCK_MONOTONIC` start time:
180-second nominal emergency deadline with a 30-second finalization reserve.
A phase is refused unless its entire requested subprocess timeout fits before
the reserve. Refusal returns 124, without spawning the subprocess. Clock errors,
invalid timestamps and an uninitialized start fail closed.

Admission is checked before each normal probe, again after its pre-probe
snapshot, before each 3-second partition-identity subprocess, and before the
lab partition mount (15-second admission margin, **not a mount timeout**).
The existing identity/unique-partition checks, supplier ordering, failure
handling and restricted lab-only writable path are preserved.

## Actual checks

`reports/baremetal-diagnostic-004-tests.txt` records 21 passing targeted tests:

- Original core: 5 tests.
- Real scratch logging against generated 003 and 004: 4 tests each.
- Historical storage and board source contracts: 1 test each; these are not
  hardware-execution tests.
- Actual C budget policy: 3 tests, including fractional boundaries, repeated
  elapsed-time checks, expired/invalid clocks and finalization reserve.
- Generated 004 `probe()` in a non-PID1 scratch harness: 3 tests. Real shell
  subprocesses demonstrate no marker file on refusal, and a marker plus real
  exit status 7 when admitted. No mount/module/reboot operation is invoked.

New budget tests were first observed failing for missing implementation, then
passing with the implementation. No project-wide test runner configuration was
found; these results are targeted checks, not a claim of a full-project suite.

Cross-compilation uses static ARM64 GCC with `-Wall -Wextra -Werror`. Packaging
report `baremetal-diagnostic-init-004.json` records 621 entries, all 620 base
entries unchanged, archive roundtrip verification and refusal outside PID1
on the MateBook. Archive: 24,216,770 bytes, SHA-256
`884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1`.

## Explicit limitations

This is scheduling admission control, not a wall-time guarantee. Filesystem
open/write/fsync, mount/unmount, process scheduling and kernel driver calls can
stall. In particular, the finalization reserve does not bound finalization.
The separate 180-second userspace reboot child remains best effort and can
interrupt an outstanding write; it cannot recover a kernel hard lock.

Actual PID1 execution, hardware initialization, persistent boot-time logging,
safe unmount/reboot and physical recovery remain unverified. PSTORE is absent;
the stale WINPE firmware entry is not a verified recovery medium. SDK7 identity
ABI gaps remain unresolved. This artifact is neither HarmonyOS-compatible nor
hardware-boot-ready by virtue of passing these tests.
