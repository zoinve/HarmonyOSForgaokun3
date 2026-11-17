# Read-only USB node planner180

Date: 2026-11-16. Source component only, not a native180 boot candidate.

## Native Bootstrap Contract

Working173's runtime source mounts genuine devtmpfs, snapshots its device
metadata, then recreates selected nodes in a private tmpfs. Its block-node
snapshot explicitly permits only loop0..4; it separately creates five loop
nodes under `/dev/block`. Thus the bootstrap does not prepopulate physical USB
block nodes. This does not establish whether original ueventd or storage_daemon
would later create them; no completed native boot with this U disk reached
original init. Native175 refused before that handoff.

The original149 storage configuration records a root storage_daemon with its
existing wrapper, permissions and security context. No daemon configuration or
ownership change is justified by the initial snapshot filter alone.

## Implemented Component

`usb-node-plan-180.h` implements two separate steps, neither integrated yet:

1. `usb180_plan` selects the exact175 USB identity/capacity through genuine USB
   subsystem ancestry. It inventories only the selected whole disk and direct
   sysfs partition descendants, not name-prefix matches. It rejects ambiguous
   disks, writable metadata, duplicate device or partition numbers, invalid or
   out-of-bounds partition extents and more than32 candidate nodes. A refusal
   returns an empty plan, not a partly admitted inventory.
2. `usb180_validate` reopens listed real nodes relative to a caller-supplied
   device-directory fd using O_RDONLY, O_NONBLOCK, O_NOFOLLOW and O_CLOEXEC.
   It requires block type, matching major/minor, exact BLKGETSIZE64 and
   BLKROGET1 for every node. Descriptors close on all tested failure paths.

Neither function creates a node, mounts media, reads disk contents, changes a
kernel write-protection flag, exports serials or writes media. Metadata planning
alone is not admission: the per-node ioctl validation is also required.

## Verification

`usb-node-plan-180/result.json` records source hashes and all test counts:

-10 planner tests, including real sysfs-tree fixtures and mocked block ioctls.
- ARM64 static compilation with -O2 -Wall -Wextra -Werror, then qemu-aarch64
  execution of both validator-failure cases and fixture metadata selection.
- Existing175 guard3 tests,176 tracing4 tests and174 observer4 tests pass.
- Total21 tests. No actual USB medium or original service was exercised.

The first test attempt failed all seven then-existing cases at fixture
compilation due to misleading indentation. The fixture was corrected; this
was not counted as a passing run. Successful final output is preserved under
the180 report directory.

## Integration Gates

Do not yet add this component to the runtime or claim file-manager support.
First obtain176 operation-specific evidence for the failed175 protection, then
observe actual service-root USB nodes and original storage events with the real
medium attached. If original services already create suitable nodes, avoid
duplicate projection and use this component only for validation. If projection
is needed, it must remain exact-device-only and opt-in, preserve original
service contracts, account for unplug/replug and dev_t reuse, and never expose
NVMe or change unknown media to writable. This component's point-in-time checks
are not a hotplug/race-proof access-control mechanism.

Working173 runtime, original images, persistent desktop data, firmware, boot
entries and Ubuntu default are untouched by this source-only step.
