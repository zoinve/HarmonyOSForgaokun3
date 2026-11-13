# Original samgr exec probe 026: fixture mount blocked transition

026 failed and its result remains `runtime_verified: false`. All preceding original-policy enforcing, device ABI and read-only filesystem checks passed. No SDK service was ready.

The child set the original configured UID/GID and requested the original configured `u:r:samgr:s0` exec context, but the kernel denied `process2 { nosuid_transition }` from `init` to `samgr`, followed by `security_bounded_transition`. The executable therefore did not enter its destination domain. The cause was the probe's retained `nosuid` mount option, not a missing token/Binder implementation.

`baremetal-sdk-original-fstab-001.json` records the unmodified vendor `/etc/fstab.hmos.emulator`: the SDK system image is mounted at `/usr` with `ro,barrier=1`; its `/data` mount separately uses `nosuid,nodev`. The read-only system mount does not specify `nosuid`.

027 uses a fresh prepared init and fresh result directory to match those read-only system exec semantics. It retains the read-only QEMU backend, `ro,noload,nodev`, the unmodified production policy and enforcing mode. It also requires the original `samgr` file to have no setuid/setgid bits. This does not grant `nosuid_transition` in policy, disable SELinux, change host mounts, or modify an original image. The `noexec`/`nosuid` read-only inspection phase remains a separate, earlier check.

026 verified the entire original image unchanged after the failed test: SHA-256 `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`. Test kernel, configuration and critical source hashes were unchanged. No MateBook reboot or Ubuntu configuration change occurred.
