# Persistent native /data

User request: mount HarmonyOS /data on real disk, preserving the working desktop.
This is an adaptation-storage change, not an OOBE or package-verification change.

## Storage

The original four immutable image files stay on the read-only Ubuntu mount.
LAB is /dev/nvme0n1p4, ext4 UUID 00029cdd-1748-4d2f-b73b-8e8164922098.
Its new root-only directory harmony-persistent-data-165 contains data.ext4,
an 8 GiB fully preallocated file seeded once from the hash-verified original
512 MiB seed. Offline growth and read-only filesystem checking completed.
No partition table was changed. LAB had 27,688,820,736 bytes free before
provisioning and 19,098,857,472 bytes afterward.

The candidate verifies LAB's mounted device, root-owned directory/file modes,
file type, link count, capacity, allocation, ext4 magic and filesystem UUID.
It holds an exclusive advisory file lock and verifies the configured writable
loop device's backing inode/device against that held file. Original image loop
devices remain read-only. There is no boot-time seed copy or truncation.

## Lifecycle

The runtime mounts loop3 at /data with ext4 ordered journaling. Five specific
adaptation-owned diagnostic objects are archived by rename under a unique
native boot ID before original services start; application/service directories
are not reset or removed. A fsynced boot marker allows two different operational
boots to demonstrate continuity without exporting user data.

The bounded test still kills its isolated PID namespace at the original budget.
After that exit, a bounded worker mounts the data loop, syncs and unmounts its
filesystem, then fsyncs the backing file and syncs LAB. A forced watchdog reboot
can still interrupt writes; ext4 journaling is not a guarantee against all loss.
Return checks require an inactive data loop, read-only offline e2fsck success,
clean filesystem state and a disk marker matching the native runtime boot ID.

## Verification And Rollback

Candidate 166 uses the verified live-debug164 helper unchanged. Its first build
failed only because a previously generated include was absent from the include
path; that build evidence is retained. The distinct compile-fix-1 build includes
the byte-verified original generated header. Fifteen focused test scripts,
reproducible ARM64 compilation, refusal guards, and the complete 29-archive
reconstruction passed before installation.

The original seed and RAM-backed 164 payload remain intact. Ubuntu remains the
persistent default. Follow the user-required latest-two-entry policy; preserve
all shared payloads even after their old entry files are archived. Operational
results must be recorded separately; provisioning or admission alone does not
prove actual /data persistence or desktop interaction.

EFI space was obtained by archiving the unreferenced 049 initrd with matching
hashes before removal. Evidence: efi-unreferenced-cleanup-004. All other EFI
files, configurations and firmware variables were verified unchanged.
