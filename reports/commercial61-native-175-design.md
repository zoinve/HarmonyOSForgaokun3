# Protected original USB storage diagnostic 175

Latest physical device observation: USB346d:5678, whole disk61849600 sectors,
removable1, nominal29.5GiB. The main partition is NTFS. Original system image
contains mount.ntfs, fsck.ntfs and blkid; availability is not execution evidence.

Preserve all 173 runtime bytes, application data, original services, private
device-root filtering, security checks and the tested persistent172/173 teardown.
Only the outer diagnostic and its hash wrapper change. Reuse the 174 observer.

Before preparing persistent data or launching original init, require explicit
harmony.usb_readonly175=1. Select exactly one whole disk with a genuine USB
subsystem ancestor, observed VID/PID, removable flag and exact capacity. An
internal NVMe disk never matches a PCI-only ancestry. Refuse ambiguity, changed
metadata, malformed device identity or missing disk after bounded discovery.

Open the selected node O_RDONLY|O_NOFOLLOW|O_CLOEXEC, verify block type, device
number and byte capacity, read BLKROGET, set only BLKROSET=1 if needed, and require
a second BLKROGET=1 before continuing. Never request write enabling. This is a
per-kernel write-protection flag, not a write to disk contents. Record the
original flag; after reboot collect fresh Ubuntu metadata instead of asserting
that the flag persisted. No media fsck, format, mount or application file test is
requested in this candidate. No new physical block nodes are exposed.

The observer records USB ancestry/VID/PID/block metadata, original-root node
matches within depth4/1024-entry bounds, original helper presence and fuse node
presence. It exports no serial, label, UUID, directory or file content. Raw
descriptor/API calls and kernel enumeration are not native file-manager access.

175's first ARM64 build failed strict maybe-uninitialized diagnostics. Its build
directory and compiler log remain preserved. Initialize selection outputs and
use the independent175-compile-fix-1 build/report; do not overwrite that failure.

Require the full archive-chain/reproducibility/guard suite and both USB observer
and write-protection tests before installation. Keep Ubuntu default, working173
entry and only the latest two installed experimental entries. Protect originals
and preserve numbered evidence. Run only one bounded operational boot, then
retrieve/hash evidence, verify preservation and check persistent data offline.
