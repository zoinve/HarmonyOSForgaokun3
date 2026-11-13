# Original SDK Binder/token reconciliation

## Evidence, not interface-name inference

The original SDK `Image` has SHA-256 `c0b82fc9dca3b83b5e8201a376b9920d9b53b2be158e8f790835ad3f1d56bbe9`. It was inspected read-only. Its access-token dispatcher accepts commands 1–8, uses ioctl type `A`, rejects null pointers and wrong types with `EINVAL`, and returns `EOPNOTSUPP` for command 0 and numbers at least 9. Thus this image itself does **not** implement parent-token command 9 or SPM commands 16–25.

The function pointers are zero in the unrelocated image, not absent: eight `R_AARCH64_RELATIVE` relocations resolve the dispatch table. The order is get/set self, get/set first caller, add/remove permission, get/set permission. See `baremetal-sdk-identity-fallback-001.json` and `baremetal-sdk-identity-original-kernel-001.json`.

`SpmGetVersion` in the original userspace writes output version zero on ioctl error and returns errno. This demonstrates a version-zero failure path, **not** that every SPM caller has been audited or that full boot is ready. Do not implement unsupported operations as success.

## Binder contract

Original kernel disassembly and extracted original IPC libraries agree on:

- Binder protocol version 8.
- Feature ioctl `0xc008621e`, eight-byte result, feature mask 5: access token and real sender PID.
- Access-token ioctl `0xc020621f`, 32-byte layout: two token IDs followed by two reserved 64-bit words.
- Sender-info ioctl `0xc0286220`, 40-byte layout, PID at byte offset 32.
- Transaction creation reads the actual sending task's token and first-caller fields. Delivery writes transaction fields into the receiving thread's cached identity.
- The original IPC userspace saves its invoker identity around transaction dispatch and restores it after dispatch/reply. This is separate from the kernel thread's last-delivered cache; do not invent a different restoration contract without testing nested transactions.

The bounded instruction scan in `baremetal-sdk-binder-token-delivery-001.json` includes unrelated stores with the same numeric offsets. Only the paired stores at `0xaa88c0` and `0xaa88cc`, in the transaction delivery path, are treated as identity-cache evidence. Numeric struct offsets alone do not establish object identity; creation and delivery use different pointer bases.

Sources: `baremetal-sdk-binder-original-kernel-001.json`, `baremetal-sdk-binder-token-lifetime-001.json`, `baremetal-sdk-binder-token-delivery-001.json`; extracted, hash-recorded `libipc_common.z.so` and `libipc_single.z.so` disassembly.

## Isolated port and regression scope

Candidate 002 retains the reference driver's authorization rules, genuine task identity fields and permission table. Its changes are limited to observed unsupported-command errors and safe device/cache initialization and cleanup. No token minting, permission bypass, authentication database change or SDK-library patch is introduced.

`test-baremetal-token-driver-002.py` executes the actual driver C handlers with host replacements for kernel primitives. The unmodified reference failed unsupported-command, live-node cleanup and failed-initialization cases; its authorization case passed. The adapted driver passed all four case groups, including root/owner/render-spawn rules, first-caller group authorization, permission-manager UID checks, actual bit changes, missing entries, 2,048-opcode bounds and the 500-node quota.

These are host behavioral tests, not real kernel ioctl, namespace, concurrency or Binder transaction tests. The isolated ARM64 object build is a separate check; no port is installed or booted by that build. Full image/link verification and live nested/one-way/reply/death/denial tests remain required before ABI readiness can be claimed.

## Object build result

`baremetal-identity-candidate-002/result.json` records successful AArch64 compilation of real `binder.o` (144,912 bytes) and `access_tokenid.o` (13,104 bytes). The native baseline configuration diff is exactly `+ACCESS_TOKENID y`. The checked original source hashes and baseline configuration remained unchanged. This checks compilation, not a full kernel link or live ABI behavior.

The full Image/DTB/module build was launched separately and writes `full-build.json` on completion. A static AArch64 ioctl probe has also compiled (`baremetal-identity-ioctl-probe-002.json`); it refuses non-PID-1 execution and requires both explicit test opt-in and QEMU `dummy-virt` model before opening token/Binder devices. Its planned diskless emulator run uses a separate test-only configuration adding PL011 console support, not a change to the native candidate configuration. No physical disks, network interfaces or GPU passthrough are attached. Transaction tests remain separate from this first ioctl regression.
