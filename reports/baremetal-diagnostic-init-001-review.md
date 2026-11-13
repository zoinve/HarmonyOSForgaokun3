# Diagnostic initramfs 001: offline review

## Fresh verification

- Ran `wsl -d Debian -- python3 /mnt/d/lab/HarmonyOSForMatebookego/next-experiment/test-baremetal-diagnostic-core.py`: all 5 tests passed (1.370 seconds).
- Independently rehashed the three local C/header inputs against `baremetal-diagnostic-init-001.json`: all matched.
- Read-only SSH verification confirmed `/mnt/harmony-lab` is `/dev/nvme0n1p4`, UUID `00029cdd-1748-4d2f-b73b-8e8164922098`.
- Independently rehashed the remote 24,216,232-byte `native-diagnostic-init-001/diagnostic-init.cpio.gz`: SHA-256 `bcf5fe6823911ccc3a1e534dcc3987702ce93e2caa52e511e41af28294289c95` matched.

These checks did not execute PID1, load modules, mount block devices, install a boot entry, or reboot.

## What the tests establish

The real Linux tests cover kernel/PID/opt-in gates, strict filesystem identity parsing, exclusive output-directory creation, real subprocess status/timeout behavior, and refusal of non-PID1 execution. Packaging evidence separately records preservation of the base archive and verification of all 621 archive entries.

## Remaining gates—not established by those tests

- PID1 execution with the candidate kernel, matching modules and board DTB.
- Actual device discovery timing, module initialization, and panel/input behavior.
- Persistent phase-log creation, flush and unmount under real boot conditions.
- Recovery from an early crash, blocked driver, or kernel hard lock. The 180-second userspace reboot attempt is best effort only; it may interrupt a lab write and cannot reset a hard-locked kernel.
- Physical access to a working recovery path. The stale WINPE entry is not verified recovery media; boot counting does not reset a hung machine.
- SDK 7 identity/Binder ABI compatibility and native HarmonyOS startup. No identity patch has been applied to this candidate.

The implementation's storage scan fails closed when any partition probe fails or identity is ambiguous. A refused writable mount therefore means no persistent logs, not permission to select another partition.

## Scope boundary

This remains an offline diagnostic candidate, not a verified boot-ready or HarmonyOS-ready environment. The existing preparation authorization does not authorize EFI installation, one-shot boot selection, reboot, or replacement of Ubuntu's default entry. Existing artifacts remain unchanged; hardware execution and recovery require a separately agreed boot procedure.
