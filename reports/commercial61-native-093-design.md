# Experiment 093: original-init physical hardware inputs

092 proves real model input and original public serial acceptance, but its
late client-side module load fails. Original ELF audit identifies server-only
SystemWriteParam ownership in original init, not the begetutil client or the
original engine stub. Pinned upstream init loads product parameter files before
the UDID pre-config hook. Public source similarity is not full private-binary
equivalence; observe original runtime results without fabricated APIs.

Add one small early rdinit shell entry. Keep both startup cores, original
module, existing native identity guard, original service identities, packages,
permissions, lifecycle, networking and images byte-identical. Verify core and
RAM parameter hashes, genuine sysfs and physical board, vendor, bounded model,
matching nonplaceholder product/chassis serials and the previously audited
physical serial hash. Refuse existing identity keys in the RAM input. Change
only RAM model plus boot.sn before original init consumes them. Create the
temporary file with umask 077 and noclobber before opening it, keep mode 0600,
and bind read-only through the existing bootstrap. No serial argv/log output,
UDID calculation, replacement verification, activation flag or credential edit.

The unchanged 091 helper observes original GetDevUdid and all original hardware
gates later. A valid existing identity is preserved without writes. No valid
identity, module load or API return alone establishes commercial activation or
a stable interactive desktop. Retain full-resolution frames and original
watchdog/IPC evidence, including the collaboration query stall seen in 092.

Hash an original valid devUdid parameter only for privacy comparison, without
printing or storing its raw value. Before export, scan raw evidence on-device
for the physical serial and matching original-UDID candidates, refusing export
if either is present. Preserve original evidence and hashes. Privacy-digest
tests and raw-input fixtures use synthetic values, never physical identifiers.

ESP has 32 MiB plus 4096 bytes free after 092 retention. Archive/remove only
old entry 091 first, retaining 092, Ubuntu default/manual entry and all shared
payloads. Put the under-one-cluster overlay at the new, unique path
`/commercial61-native-092/early093.img`, reusing an existing directory without
modifying its original initrd. This avoids a new directory allocation. Require
space for two clusters (overlay and entry) above 32 MiB and verify final free
space at least 32 MiB. No guard reduction or payload deletion. Final entries
are 092/093; record the pre-install removal separately under standard retention
evidence. Install and boot once only, then retrieve before preservation checks.
