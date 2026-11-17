# Native 166: real-disk /data and clean return verified

One bounded operational boot completed, without retry:
commercial61-native-087-054d8bc8-bc93-407a-ab6c-85b00eb7658c.
Start 2026-11-16 07:10:24 UTC; Ubuntu return 07:14:08 UTC.
Build/admission/results are under commercial61-native-166-compile-fix-1.
The original failed local compilation is preserved under commercial61-native-166.

## Storage Evidence

The runtime verified its 8 GiB writable loop against the held NVMe backing inode,
mounted ext4 on /data and handed off to the original init. No seed reset or RAM
data mount occurred. The first native boot marker was committed to the filesystem.
The bounded exit worker reported inner syncfs, unmount, backing fsync and outer
syncfs success. All 182 retrieved files matched their remote hashes.

After return, the inactive data image passed read-only offline e2fsck with exit
zero and reported a clean filesystem. Its marker matched the native boot ID,
not the returned Ubuntu boot ID. This proves the first write reached disk, not
yet that a second native boot can reuse it.

The authenticated read-only native diagnostic connection passed unchanged;
MMI holds touch and storage modules are live. This does not establish physical
input or original USB-service acceptance.

## Desktop Caveat

The first persistent boot installed com.ohos.sceneboard successfully through the
original BMS (resultCode 0), but the inherited desktop script checked for its
process before that completed and exited with OOBE114_MISSING_EXISTING_SCENEBOARD.
Composer produced valid nonblack frames early, but no persistent-boot desktop
acceptance is claimed. The second boot must check the retained install and
normal desktop startup. No signing check, package or identity was bypassed.

## Preservation

Ubuntu returned as current/default with boot ID e19ecd1d-e3d5-450f-9fa4-a3a0a39e5632.
All four original images and firmware variables were unchanged, screen-off timer
enabled/active, LAB unmounted. Latest entry retention archived entry161 and kept
164/166; shared payloads remain. The obsolete unreferenced049 payload was backed
up before installation in efi-unreferenced-cleanup-004, outside the installation
journal's baseline.
