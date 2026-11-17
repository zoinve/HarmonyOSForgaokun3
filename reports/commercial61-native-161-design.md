# Native 161: attribute pre-SSH storage failure without EFI payload deletion

Native 159 passed root/address/config/socket creation but exited 93 before SSH.
Fixture 160 proved the unchanged bind/key functions work inside separate native
Ubuntu mount/PID namespaces, including enforced read-only binding and live append
visibility. The failing native substep remains unknown; do not guess permissions,
FD loss, network failure or key corruption.

## Deliberate scope

Keep native init 159 and original service/runtime/seed/driver artifacts bit-for-bit.
Replace only the RAM /live-debug159 executable with a BusyBox loader in a new
538-byte compressed overlay. Append this after the unchanged 159 chain: 29 archives
total, complete ordered merge verified against the expected full initrd.

The new helper is stored separately on Ubuntu, root-owned mode 0500, and is not
placed on ESP. The loader requires the inherited exact native arguments and both
regular log FDs, checks the source SHA-256, copies exclusively to an absent RAM
destination, checks the RAM SHA-256 and execs it. There is no new shell command
surface for a remote client, no image patch and no unsigned executable admission
into original HarmonyOS services. Existing native 159 opt-in remains mandatory.

Helper SHA-256: 612b2db0a56a884680492987dbdc0ce135a7a4a660aeb55ecfd367b0b7a33f05.
Its generated source and storage-header hashes are recorded in result.json.
No literal hash transformations are used when adapting numbered workflows.

New fixed item/stage/errno records distinguish source-FD/type, destination lstat/
empty-file check, bind/remount/statvfs/read-only flag and key open/metadata/
destination/read/write/close. No key material, raw logs, keyboard content or USB
serial is reported. Existing authentication, fixed reader, distinct RAM root,
private mount/PID namespaces, target-network-only join and bounded cleanup remain.

## Admission and preservation

Sixteen focused/baseline scripts pass; helper regeneration and static recompilation
are byte-identical; non-native guards refuse execution. Loader tests use a labelled
synthetic host payload and prove hashing, exclusive destination and FD propagation,
not a native HarmonyOS connection. Two separate analyzer regression tests require
the inherited original context, new helper/storage/loader evidence and actual
authenticated current-address observation before accepting runtime success.

The compact overlay avoids deleting any previous EFI payload or reducing the
32 MiB reserve. Installer still verifies all old EFI hashes, kernel/DTB, firmware,
Ubuntu persistent default, active screen-off timer and no pending one-shot.
Only latest-two entry retention is authorized, with removed entries archived.
One bounded diagnostic boot may follow installation and checks; no repeats.

Successful transport would not itself prove full debugger attachment, physical
touchscreen operation, original USB-service acceptance or a Settings repair.
The full basic-driver objective remains active, with touch and USB priority.
