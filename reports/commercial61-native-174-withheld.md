# USB storage diagnostic 174: built, not installed

The observer adds bounded read-only USB mass-storage sysfs metadata, a scan for
matching block nodes in the original target root, original NTFS helper metadata,
and /dev/fuse presence. It observes late execution as well as startup. It does
not expose new device nodes, open raw blocks, mount media or read USB serials.

Four focused observer tests and the full 19-script admission suite pass. Static
ARM64 rebuilds reproduce exactly; the complete 29-archive chain reconstructs the
full initrd. Original runtime173 is byte-identical, including the repaired data
lifecycle and original launch logic.

174 is intentionally not installed or booted. Candidate175 adds explicit kernel
write protection for the user's confirmed removable USB disk before original
services start. This prevents the diagnostic from depending solely on presumed
absence of automatic storage actions in original services.

The observer's node traversal is bounded to depth4 and 1024 entries per block
identity. Its node_scan_complete field reports entry-budget availability, not
proof that no matching node exists beyond its depth bound. Zero matches must be
reported as zero within that bounded scan, not exhaustive absence from all paths.
