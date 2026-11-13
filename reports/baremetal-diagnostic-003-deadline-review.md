# Diagnostic 003: deadline and recovery review

## Scope

Static review of generated 003, not a hardware boot test. Existing archives,
boot entries, watchdog configuration and operating systems are unchanged.

## Budget mismatch

The independent best-effort reboot child sleeps 180 seconds. The parent has
individual command timeouts, but no shared remaining-time budget:

| Work | Configured command allowance |
| --- | ---: |
| PCIe PHY and NVMe | 2 × 15 = 30 s |
| Scan up to 64 partitions and recheck selected lab partition | 65 × 3 = 195 s |
| Seven post-storage board modules | 7 × 15 = 105 s |
| Enumeration and kernel log | 10 + 5 = 15 s |

These allowances sum to 345 seconds, before other work. This is a conservative
sum, **not** a measured duration or a simultaneously attainable path: failed
identity checks refuse disk logging, and module timeouts stop later module
probes. Nevertheless, nothing enforces completion of the entire parent within
180 seconds. Even successful commands can consume much of their allowance.

`snapshot()` performs synchronous writes and `fsync`; filesystem mount,
directory synchronization and unmount are also not bounded by `diag_run()`.
Thus the command allowance sum is not an end-to-end upper bound.

## Consequences

- The emergency reboot can overlap a parent operation, including lab log writes.
- A command timeout does not prove that a kernel-blocked child was reaped.
- Successful `modprobe` does not establish completion of deferred device probes.
- Sleeping userspace cannot recover a kernel hard lock. No hardware watchdog
  recovery has been exercised, and pstore is absent in this candidate config.
- Existing boot counting is not a timer. The stale WINPE firmware entry is not
  a verified recovery medium.

## Before a first hardware trial

Review a shared parent deadline with reserved finalization time, stop scheduling
new work when the reserve is reached, and specify what happens when persistence
or unmount cannot finish. Merely increasing the sleep is not a recovery fix.
Any future revision must retain exact lab-partition identity checks, refusal on
ambiguity, original-data protection and unchanged watchdog/security policy.

No implementation change, installation, reboot or boot authorization is implied
by this review. Actual PID1, device probing, persistent logs and recovery remain
unverified. Diagnostic 003 is not HarmonyOS startup.
