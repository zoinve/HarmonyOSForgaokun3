# Experiment 092: real early hardware model input

091 original APIs establish an empty boot serial/UDID and a runtime product
model conflicting with actual physical DMI. Manufacturer already matches.
092 changes only the RAM product model input before original init loads it.

Select a small explicit rdinit shell entry instead of replacing the existing
outer /init. Require root/PID1 and the exact unchanged original core hash.
Mount genuine kernel sysfs at an otherwise unused RAM directory. Require
the actual MateBook device-tree model, valid bounded firmware product/vendor,
sysfs filesystem magic, exact original RAM parameter hash, and one matching
manufacturer and model key. Rewrite only the RAM model value from actual DMI;
never read a serial or calculate an identity in this wrapper. Unmount temporary
sysfs and exec the original unchanged /init as PID1. The existing bootstrap
later binds this RAM file read-only and launches the unchanged original init.

Keep original 091 public-API/firmware identity guards and refusal semantics,
including original module and helper hashes, native API permission checks,
and no substitution for a failed SetParameter or GetDevUdid. An absent serial
may only be supplied through the already reviewed original API gate. Network
refresh and original desktop/service observation remain. No guide force-stop,
fake provisioning, synthetic identity, private binary patch, new permissions
or original image writes. Identity validity is not activation completion.

Tests use synthetic fixtures only, with exact initrd AArch64 BusyBox applets
under qemu-user; filesystem-type syscall is simulated for those fixtures.
They are not native boot or desktop proof. Target early status is copied into
the existing diagnostic log. Retrieve only after an on-device exact physical
serial scan passes, without exporting the serial; original raw files/hashes
remain intact. Retrieve first, then serial preservation verification.

Preserve Ubuntu default, manual entry, firmware, original images, screen-off
timer, shared payloads and all numbered history. Keep only entries 091/092
after archiving entry 090. Preserve the 32 MiB ESP guard, using a measured
overlay under 4096 bytes, not a duplicated large core. One bounded boot only.
