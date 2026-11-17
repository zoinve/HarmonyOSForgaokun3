# Commercial 050 closure

The only boot ran 2026-11-14T14:35:09.475375Z through 14:38:51.537156Z,
returning to Ubuntu boot b62e7e6e-4784-4386-8922-4f7140037ec2. All 82 raw
files match remote hashes after ro,noload retrieval. No journal replay was
needed. Original target timeout and target exit status 9 are recorded, and
the hardware observer stopped before target cleanup. Do not repeat 050.

Kernel 045 and all of its original module bytes were reused. Offline wrapped
perf sample, register layout, loss and partial-header tests passed. Full 050
differs from full 045 only in outer init; original bootstrap, userland and
modules are byte-identical. Fixed incremental archive chain equivalence and
workflow safeguards passed. These tests do not prove runtime attachment.

Original SceneBoard installed and ran. There are no missing-application-agent
warnings. First ArkUI flush is at guest 81.752 seconds; last composer frame
is at 77.763675 seconds, with zero observed post-flush frames. All seven
160x256 scanout exports contain only black pixels. Native desktop pixels and
interaction remain unverified.

The observer found actual original RS global PID 1245 but all 19 mapping
attempts returned EAGAIN. No hardware event attached and no perf sample exists.
Neither unsupported hardware nor nonexecution of original methods can be
inferred. The unresolved interval is in mapping identity/address resolution,
not a reported perf_event_open failure. Counts of zero are not coverage.

Existing inner diagnostic maps show the original library executable mapping.
The current resolver incorrectly assumes that the root-path fstat inode and
device must equal the backing-file identity in proc maps. The bootstrap mounts
/system via OverlayFS, and the exact 045 kernel ovl_mmap calls backing_file_mmap,
which installs its real backing file as vm_file. Synthetic overlay identity
is therefore not a reliable mapping identity gate. Actual root-path and mapped
identity differences were not logged in 050, so the precise rejection is not
yet independently established at runtime.

The next resolver must verify the actual map_files file, its maps inode/device,
audited entry instruction and full byte equality with the audited root-path
library. Do not merely remove inode validation or attach to a guessed address.
Its offline tests should accept identical bytes with different source inodes
and reject a one-byte change. Actual map_files permissions and perf support
remain runtime questions.

Post-return verification passed: 112 prior EFI files unchanged; normal random
seed update and archived authorized removal of entry 048 accounted for;
firmware and four original commercial images unchanged; Ubuntu current/default,
original manual entry, unmounted lab partition and enabled/active screen-off
timer retained. Experimental entries remain 049 and 050 with shared payloads.
