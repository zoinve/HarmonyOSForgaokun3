# Live radio checkpoint 557

Date: 2026-11-17. Overall hardware-driver goal remains active/incomplete.

## Current Device State

Read-only rechecks still cannot reach Ubuntu SSH or discover a native debug
endpoint after the532 observation timeout. No additional boot, remote command
execution, host configuration change, data mount or device write was performed
in this continuation.532 has not been rerun and its missing logs have not been
replaced by logs from another candidate. Its screen/reboot/network state is
unknown pending external recovery or a user screen-state observation.

Inspection of the actual532 init source confirmed the independent900-second
userspace reboot helper is present and armed before module/storage IO. The
source explicitly states it is not a hardware watchdog and cannot recover a
wedged kernel. This does not prove the helper fired or that the kernel wedged.
Do not change reboot logic based solely on the current SSH timeout.

## Prepared Numeric Radio Query

Reader551 adds only the exact read-only command radio-status to the original
restricted SSH command dispatcher. It reads the original native diagnostic log
through the existing no-follow/regular-file guard, scans at most64MiB, and emits
only bounded numeric interface/start/PONG observations. It never issues P2P
control commands, executes a supplied command, or exports raw logs, SSIDs,
MAC addresses, passwords, keys or input events.

The output records missing observations as -1, reports incomplete snapshot
reads, always states current_connection_not_proven, and leaves transfer
acceptance false. Historical PONG is not proof of a currently working link.
The original status/settings/follow-settings commands and exact argument
restriction remain intact. No existing live endpoint was modified or bypassed.

## Tests And Packaging

- Reader552: ten original/new tests passed, covering command injection,
  privacy, symlinks/FIFOs, binary/overflow records and bounded reads.
- Sanitizer554: all ten tests passed with ASan/UBSan.
- Build553: static ARM64 reader compiled; four QEMU command-dispatch checks
  confirmed forbidden commands remain refused and an absent log is not success.
- Candidate555: built locally, not installed or booted. Retains backend543
  (official2.12), kernel490/matching modules500 and the private controller probe.
- Integration556: five tests passed. Its installer was exercised in temporary
  directories with the actual public reader payload. Normal copy/verification
  succeeded; bad digest, source/bin/target symlinks and stale temporary files
  were refused while preserving the existing reader.

The new reader is a separate public payload. The optional loader verifies
its bytes, copies it into RAM, checks the copy and atomically replaces only
the jailed diagnostic reader. Authentication files, SSH configuration, keys,
forwarding/TTY restrictions and the original runtime archive are unchanged.
Candidate555 supersedes the prepared546 candidate but neither is installed.

These are local source/build/fixture results, not hardware acceptance. No
Share transfer, native cgroup enforcement, compatibility-platform application,
physical volume-down, CPU frequency UI, multitouch, acoustic audio or120Hz
success is claimed. USB work remains preserved/paused. Resume by verifying
the real device identity, retrieving532 without journal replay, checking
Ubuntu boot protection and analyzing its actual P2P results before choosing
another operational candidate.
