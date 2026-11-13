# Bare-metal diagnostic recovery contract (offline draft)

## Scope and evidence

This is a preparation document, not a boot installation or a verified recovery path.
Inputs: `baremetal-diagnostic-recovery-preflight-001.json`,
`baremetal-recovery-boot-audit-001.json`, and `baremetal-initramfs-base-002.json`.
No reboot, EFI edit, module load, authentication change, or SDK image change is authorized by this document.

The verified base archive has SHA-256
`ff0a661c831f950ebad0cd69c91b21d999bffce6f2bc49601e2cb7253ab5219c`.
It contains 391 candidate modules and 12 board/Adreno firmware files, but **no `/init`**.
It is not a complete bootable diagnostic environment or a HarmonyOS-compatible kernel.

## Storage boundary

Only the dedicated lab filesystem may receive diagnostic writes:

- filesystem UUID: `00029cdd-1748-4d2f-b73b-8e8164922098`
- GPT PARTUUID: `24bd14b9-9d92-490a-ad15-a59c6b8e7cd9`
- expected partition: `/dev/nvme0n1p4`

Before any writable mount, a future PID1 must independently verify BOTH identifiers,
ext4 type, and candidate kernel release `7.1.0-rc3-gaokun3-el2`.
Device numbering alone is insufficient. Missing or contradictory identifiers must
disable disk logging, not trigger formatting, repair, partition changes, or fallback
to another filesystem. Never mount Ubuntu, EFI, or swap as diagnostic output.
Create a new exclusive run directory; never reuse completed run directories.

## Proposed first diagnostic sequence

1. Require PID 1 and an explicit diagnostic-only command-line opt-in.
2. Mount only proc, sysfs, and devtmpfs in the isolated initramfs.
3. Record kernel release, command line, device-tree model and phase markers in RAM.
4. Resolve and load only matching candidate NVMe dependencies, with a bounded wait.
5. Verify the lab partition identifiers before mounting it `nodev,nosuid,noexec`.
6. Save phase markers and kernel messages to a new lab run directory, syncing each phase.
7. Probe candidate panel/MSM/input dependencies in separate bounded phases; capture
   actual DRM connector states, modes, device nodes, and input enumeration.
8. Save final status, sync, and cleanly unmount lab storage before a planned reboot.

This first diagnostic does not start HarmonyOS, expose a network shell, change
SELinux mode, open `/dev/watchdog`, or mount SDK userdata. It must not report a
desktop, working GPU, input alignment, or identity compatibility from enumeration alone.
No changes to existing watchdog protections are part of this work.

## Recovery limitations and gates

- The baseline has `CONFIG_PSTORE` disabled. RAM logs disappear on reset, and lab
  filesystem logging cannot capture failures before NVMe becomes usable.
- A userspace deadline cannot recover a kernel hard lock or uninterruptible I/O.
  An elapsed timeout is not proof that a blocked task has terminated.
- Existing systemd-boot supports one-shot selection and boot counting. Neither
  capability has been exercised for this candidate. Boot counting is not a timer
  and cannot itself reset a hung machine.
- Ubuntu standard kernel remains the configured default. Any later boot experiment
  must preserve that default and independently verify its kernel/initrd/DTB exist.
- The stored `F10WINPE` firmware entry references PARTUUID
  `715f26be-6827-45d4-8b22-587eaf208b50`, which is not in the current disk inventory.
  Do not count that entry as a verified recovery medium and do not modify it here.
- Hardware reset/menu access and early-crash capture remain unverified. A future
  boot must explicitly account for SSH loss and the possible need for physical recovery.

## Required offline tests before packaging PID1

- Refuse non-PID1 execution, absent opt-in, and kernel-release mismatch before side effects.
- Reject missing/mismatched UUID, PARTUUID, type, or conflicting device matches.
- Reject a pre-existing run directory; never follow an output symlink.
- Verify failure at each probe preserves a truthful phase/result record.
- Verify bounded normal completion and log synchronization without invoking reboot
  or loading host modules during tests.
- Reparse the final archive and verify every mode/content/hash; retain base-002 unchanged.

## Offline implementation status

Source candidate: `next-experiment/baremetal-diagnostic-init.c`, with safety helpers
in `baremetal-diagnostic-core.c`. `test-baremetal-diagnostic-core.py` executes real
Linux validation, directory creation, process-failure/timeout, and non-PID1 refusal
tests. This does not exercise hardware probing, actual mounts, persistent logging,
unmount, or reboot paths; those remain unverified.

The PID check precedes all side effects. Reading the explicit command-line opt-in
requires a proc mount in initramfs; this minimal pseudo-filesystem mount precedes
the release/opt-in checks. No module or block-device operation precedes those checks.
A refused PID1 holds rather than exiting into a kernel panic.

The candidate attempts an emergency reboot at 180 seconds independently of its
normal probe sequence. It is best effort, not a reliable kernel-hang recovery
mechanism. If normal flushing or unmount stalls, that emergency reset could
interrupt a lab log write. Only the lab partition is a writable storage target;
that restriction does not make interrupted writes safe or logs crash-proof.

Current status: offline implementation and packaging work only. Boot installation,
hardware recovery validation, persistent-log validation, and native HarmonyOS
startup remain pending. A successful build is not permission to install or boot it.
