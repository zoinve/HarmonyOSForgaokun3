# Original SDK init 036: token initialization reached, not service-ready

The original SDK PID1 now progresses beyond the immediate restart seen in 035. This is not a successful HarmonyOS boot: the external 60-second observation limit expired, and service readiness remains unverified.

## Observed

- Matching the original early-init `/dev` tmpfs layout removed the earlier generic-devtmpfs bootstrap blocker. Only genuine kernel character/block devices were mirrored; no token, entropy or parameter values were substituted.
- Original init loaded its selected developer policy, entered `u:r:init:s0`, started ueventd and attempted real native-token initialization.
- Repeated `LockNativeTokenFile` failures concern `/data/service/el0/access_token/nativetoken.json.lock`. Enforcing AVCs reject associating `accesstoken_data_file` with the simplified tmpfs `/data`; subsequent locking is also denied.
- `permissive=0` denials were retained. No policy exception, `setenforce`, fabricated native-token record or service-ready marker was introduced.

The production policy used by the earlier isolated ABI tests is **not** the policy selected by this original-init run. Do not combine those security scopes.

## Preservation

The runner verified all three original SDK images byte-for-byte unchanged, together with the storage-test kernel/config, native profile config and critical source files. MateBook Ubuntu and its boot entries were not changed or rebooted.

Serial: 67,053 bytes, SHA-256 `dc73b45d987d61efe1fee541df0a5699eea7407fa664d71191fdfae78b3e4bbb`.

Independent verification subsequently confirmed both prepared artifacts, all three complete original-image hashes, the test-kernel hash, byte-identical local/WSL reports and serial logs, and the explicit enforcing token-lock failure. See `baremetal-sdk-original-init-qemu-036/independent-verification.json`. The timeout and non-readiness classification were preserved.

## Next controlled test

037 replaces only the simplified `/data` filesystem with a newly formatted 512 MiB ext4 image backed by host RAM. Original userdata is not attached. All three original drives stay QEMU read-only and mounted read-only; scratch changes are retained privately for inspection. Original init remains responsible for policy selection, labeling, token creation and service initialization.

The original hardware boot argument and original fstab device ordering are still separate, known bootstrap prerequisites; a 037 timeout alone must not be interpreted as a complete test of them.
