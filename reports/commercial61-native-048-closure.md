# Commercial 048 recovered-evidence closure

The only boot began 2026-11-14T14:02:31.691639Z and Ubuntu was observed
again at 14:04:08.433173Z, boot ID 15104c45-648f-423c-bb50-78c63a137213.
Do not repeat this completed numbered boot. A normal target timeout is not
established, and native desktop pixels/interaction remain unverified.

This candidate reused exact kernel 047 and its matching rebuilt modules.
The original inner bootstrap was unchanged. It added persisted snapshots
before and after each tracefs control write, without changing original
service binaries, credentials, authentication, Binder identities or policies.
Build, original-userland equivalence, module closure and boot protections
passed. The ordered incremental initrd chain equals the full archive.

The first partial-retrieval attempt failed before mount because its mount
point did not exist. After fixing directory creation, ro,noload inspection
found no visible 048 run directory and unmounted. No original repair or
operational reboot was performed in either retrieval attempt.

A new independent metadata image was then created under commercial-recovery-048
on Ubuntu. Journal-only replay affected only that regular file. The recovered
root directory identifies commercial61-native-048-102fca28-dfc7-4143-8253-2aa1428b490c.
Its 42 files were recovered via replayed block mappings and original block
data read O_RDONLY, with byte counts, hashes and physical-block provenance
preserved. No prior readable 048 set existed for independent comparison;
unlike 047, a previous-set comparison cannot be claimed. The original remained
unmounted, its superblock bytes unchanged. Recovery artifacts are separate.

Hash-verified boundary-analysis.json uses phase-040.log. It shows original
outer samples 0, 1 and 2, but no durable TRACE_CONTROL_BEGIN/END, TRACE_READY,
TRACE_SETUP_FAILED, target timeout or target-exit markers. This is not proof
that trace registration or any control write did not execute. A crash, a
reset, an incomplete final journal transaction, or another early-return cause
cannot be distinguished from these records alone.

The verified return preserves Ubuntu current/default, original manual entry,
firmware and all four original commercial image hashes. There are 110 prior
EFI files unchanged, the normal random-seed update and hash-matched archived
removal of old entry 046. The screen-off timer is enabled/active and the lab
partition unmounted. Experimental entries retained are 047 and 048; kernel
and shared payloads were not removed.

Next narrow the unobserved interval before the first control write: original
process discovery, PID-namespace match, original ELF instruction validation,
tracefs mount and existing-event inspection. Persist stage boundaries before
concluding that a particular uprobe or original RenderService method failed.
