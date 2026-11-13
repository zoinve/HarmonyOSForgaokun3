# Original SDK init 037 — genuine service initialization, not readiness

## Controlled change

Replaced the hand-made tmpfs `/data` fixture with a fresh 512 MiB ext4 device backed by private RAM. This matches the original emulator fstab filesystem type and removes the observed policy `associate` failure without changing policy or inventing token records. Original userdata was never attached. Original SDK init remained PID 1 and performed its own parameter, policy and native-token initialization.

All three original SDK drives remained hardware read-only. The unchanged storage-test kernel SHA-256 is `5968eea1728b4edd2a9bc898ef3c2fb39cf0e3ffbcb5f686b318c90be601604d`; SELinux was active with `enforcing=1`. Original init selected its original **developer policy**, not the production policy used in earlier isolated tests. Do not conflate these scopes.

## Observed

- Original SAMGR entered `main` at about 13.50 seconds, initialized its profile, and began SA registrations at about 14.34 seconds.
- The retained serial log contains 43 `SAMGR: insert SA:` records. This is a log count, not 43 independently verified operational services.
- Neither `LockNativeTokenFile` nor `get tokenid failed` appeared, unlike trial 036.
- Policy denials remained visible with `permissive=0`; none was bypassed.
- The external 60-second observation deadline terminated QEMU. `runtime_verified` and `services_ready` remain false: no successful independent Binder readiness query or desktop was established.

## Evidence and preservation

`baremetal-sdk-original-init-qemu-037/independent-verification.json` independently confirms prepared-file sizes/hashes, exact local/WSL result and serial equality, the kernel, all three whole original image hashes, and the retained private scratch image. Serial SHA-256:

`a3068191c6c413d4b65c6238ba4c71969b19d0be0754f685b571319e9c1d675a`

Scratch evidence is retained privately in the WSL work directory as `scratch-data.ext4`, SHA-256:

`3d050ea587e889387b11645dd042bbdb49aa1bb247159eb7917efaa1cd6275fe`

Its metadata is **not verified**: read-only debugfs inspection reported a block-bitmap checksum mismatch after the forced stop, despite returning exit status 0. No token-file contents were read, and no repair was performed on this evidence. A later recovery examination would require a separate copy, not modification of this retained image.

Original system/vendor/sys_prod images, native configuration, test kernel/configuration, and guarded source files remained unchanged. No physical MateBook reboot, Ubuntu modification, network or GPU attachment occurred.

## Next bounded test

038 supplies the original `ohos.boot.hardware=hmos.emulator` and arranges virtual disks to match the unchanged original fstab. Serial, capacity and exact device-name guards must all pass before init handoff. It uses a new scratch image and does not rewrite the fstab, policy, libraries or authentication data.
