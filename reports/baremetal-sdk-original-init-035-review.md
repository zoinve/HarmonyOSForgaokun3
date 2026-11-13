# Original init handoff 035 — executed, not service-ready

The serial-qualified disk selection fixed 034's wrong filesystem mapping. The helper mounted actual `vdc` (system), `vdb` (vendor), and `vda` (sys_prod), then executed the unchanged SDK init as PID1. Original init logs appeared, its own policy loader succeeded, and subsequent AVCs showed `u:r:init:s0` with `permissive=0`. It nevertheless restarted at about two seconds. No service readiness or complete post-handoff enforcement audit is claimed.

Important distinctions:

- The original loader selected `/vendor/etc/selinux/prebuild_sepolicy/developer_policy`, **not** the production `policy.31` used in earlier isolated ABI checks. Neither policy nor the loader was modified. These evidence scopes must not be merged.
- `hardware` was absent from the command line and original init could not resolve its hardware-specific fstab. The original fstab also expects system on `vda`; helper serial-based mounting alone does not change that expectation inside original init.
- The handcrafted fixture used devtmpfs `/dev`. After policy loading, original init was denied directory relabelling/read/search against its generic `device` label. This is an early-boot fixture mismatch, not evidence to grant additional permissions.
- Original init's prelinker `prctl` returned `EINVAL`; this remains a separate compatibility observation, not an established fatal cause.

Independent verification compared both prepared files, all three original images, the test kernel, local/WSL JSON and exact serial bytes. The serial SHA-256 is `2e4954170401728ed0df99edd14b4357845cb86e9fe5e5341f42d97de2b10fca`. Every preservation guard passed. See `baremetal-sdk-original-init-qemu-035/independent-verification.json`.

## Controlled next observation 036

Disassembly of the original ramdisk `init_early` establishes its `/dev` mount: at `0x234d8`, source and filesystem type resolve to `tmpfs` (`0xa6ae`), target to `/dev` (`0x8af2`), flags to `MS_NOSUID`. See `baremetal-sdk-init-early-mount036-audit.json`.

036 changes only the device filesystem fixture. It first inventories real kernel devtmpfs character/block nodes (bounded to 256), unmounts devtmpfs, mounts RAM tmpfs, and recreates those same real device numbers, ownership and initial modes. It does not supply fake device services, entropy, parameters, identities or permissions. Policy loading and label restoration remain the responsibility of unchanged original init. Disk ordering and boot arguments remain those of 035 to isolate this change.

The generated C passed strict host compilation and actual non-PID1 refusal before mount/device actions. The ARM64 helper is 778,440 bytes, SHA-256 `ad15f727dcabb4fce1abc3c1d1d8a9e11aa61b40303270c204da5473335538ff`; source SHA-256 `06c2e55db62cc067e25da8cb1058f3c55a27cfe2a0d622aa7e5a435f8b1c1b3e`. Runtime observation was launched separately; this document does not predict its result.
