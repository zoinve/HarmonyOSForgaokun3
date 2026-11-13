# Original samgr exec-domain observation 027

## Verified scope

The unchanged original SDK `/system/bin/samgr` was executed with UID/GID 5555 and original supplementary groups. The parent observed its actual `u:r:samgr:s0` domain under the unchanged original production policy with enforcing enabled. This verifies the normal executable-domain transition, **not service readiness**.

The read-only guest system mount now follows the original vendor fstab's absence of `nosuid`. The original executable has no setuid/setgid bits. The failed 026 run remains preserved; no `nosuid_transition` permission was added to policy.

All preceding 027 policy-load, identity-device positive/negative, and read-only filesystem checks passed. However, samgr exited 127: its original musl loader could not find its non-libc dependencies. `runtime_verified` in this bounded probe describes the observed exec-domain transition only; `services_ready` and `services_tested` remain false. Original SDK service initialization and Binder manager registration were not verified.

## Next isolated change

Read-only image inspection in `baremetal-sdk-loader-layout001.json` confirms the original root `/etc` symlink points to `/system/etc`. That directory contains the unchanged loader search paths and namespaces. The RAM fixture omitted this link. Candidate 028 adds only the original `/etc` link; it does not replace libraries, set `LD_LIBRARY_PATH`, change original policy, or fabricate service tokens.

## Preservation

Original system image SHA-256 before/after 027: `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`. The QEMU backend was read-only and the ext4 mount used `noload`. Kernel/config/critical source preservation checks passed. No physical reboot, Ubuntu change, network device, or original SDK image write occurred.

Independent verification in `baremetal-selinux-qemu-027/independent-verification.json` checked both prepared files' sizes/hashes, the actual test kernel hash, the whole original system image hash, and equality of local/WSL result JSON and raw serial bytes. Serial SHA-256: `c9e959eba8ae43c7d10947b571ee04bf32aee58351d99d131ec96ab45f736d16`. Exit 127 and the dynamic-library errors were explicitly verified, not excluded from the success scope.
