# Identity candidate 002: first real-kernel regression

## Verified scope

The complete ARM64 native candidate built successfully in its separate workspace. Five kernel artifacts were independently checked against their recorded sizes and SHA-256 values, and all 391 modules were inventoried with matching `7.1.0-rc3-gaokun3-el2` vermagic. This is not an installation or a physical-board boot.

`baremetal-identity-qemu-002/result.json` records a successful diskless QEMU run of a separately built PL011-console-enabled test kernel using the same patched source. The native candidate configuration and critical source hashes remained unchanged. The guest had no attached disks, networking or GPU.

The actual static ARM64 PID-1 program reported:

```
IDENTITY002_PASS checks=51 transactions_not_tested=1 desktop_not_tested=1
```

Checks exercised the real kernel handlers, including self/first-caller 64-bit roundtrips, fork inheritance, unprivileged denials, supplementary-group authorization, UID-3020 permission-bit operations, root denial for permission management, invalid pointers and unsupported commands. Binderfs provided an independent device; protocol 8, observed feature bits 5, initial zero identities and zero reserved output fields were checked.

The deliberate test identities were created only inside this explicitly opted-in QEMU regression through the driver's existing authorized setters. No original SDK identity store, authentication component or physical-machine token was changed.

## Limits and next regression

This run does not test Binder transactions, nested calls, concurrent access, process death, original OHOS IPC libraries, native-board operation or a HarmonyOS desktop. The 51 checks are not a complete ABI conformance claim. Unsupported SDK calls return errors rather than fabricated success; userspace fallback remains a separate question.

A fresh transaction probe 003 adds separate Binder opens and caller processes, distinct caller token pairs, synchronous reply checks, receiver self-token preservation and one-way delivery after sender exit. Its compile completed without diagnostics. The optional user-mode non-PID1 execution check could not run because `qemu-aarch64` is unavailable; the failure and metadata-only completion are recorded in `baremetal-identity-transactions-003/preparation-note.txt`. No emulator was downloaded. The system-mode transaction run is recorded separately and was pending when this note was written.

Evidence: `baremetal-identity-candidate-002/{full-build.json,independent-verification.json}`, `baremetal-identity-qemu-002/{result.json,serial.log,config-diff.txt}`, and `baremetal-identity-transactions-003/`.

## Subsequent transaction results

The separately recorded 003 run subsequently passed 132 checks, and 005 passed 180 checks including a real nested callback and a changed first-caller token in its reply. See `baremetal-identity-transactions-005-review.md` for the verified scope, independent log/hash check, preserved failed 004 harness attempt and remaining limits. These results do not retroactively enlarge the scope of the original 51-check run.
