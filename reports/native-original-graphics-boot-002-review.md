# Native original-service trial 002

## Purpose and scope

User requested continued repair and autonomous verification. Trial 001's immutable
logs establish original init/policy execution and real DRM nodes, but not service
startup. Its printk rate limiting and process-name filter leave the failing
boundary unresolved. This candidate changes **diagnostic coverage only**, not EGL,
service identities, original images, board configuration or security decisions.

Added unfiltered namespace process command lines including PID 1; init status,
mountinfo, wait channel/stack/children; filesystem metadata and bounded directory
listings for data/config/device paths; and outer-namespace process status. Kernel
`printk_devkmsg=on` applies only to this temporary native diagnostic boot so early
original-init messages are retained. This is not a change to Ubuntu security.

## Preboot verification

- New test failed for the missing 002 implementation, then passed after building.
- Both static AArch64 programs compiled with `-Wall -Wextra -Werror`.
- Nine artifact hashes checked; inherited readonly-loop, namespace, board opt-in,
  genuine-device, original-credential and 180-second return gates retained.
- Real MateBook non-PID1 execution refused both programs with exit 77.
- Staging was exclusive and did not execute target services.
- Installation journal preserves prior EFI hashes. Only unreferenced, byte-identical
  kernel cache copies `harmony-native-diag-011/linux` and `013/linux` were removed;
  the retained 015 kernel, historical initrds, original images and logs remain.
- New counted entry reuses 015 kernel/DTB; 78,479,360 EFI bytes free after install.
  Ubuntu persistent default and firmware entries unchanged.

Runtime conclusions must come from collected raw logs, not successful construction
or the fact that a boot was requested. The runner allows one physical boot only.
