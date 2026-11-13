# Original FD command-word / side-vector characterization

## Verified

- `composer-fdstream-run-001`: eight cases passed in the diskless, headless,
  networkless ARM64 TCG guest; QEMU rc0, normal child exit, 19.22 seconds.
- Original service `FileDescriptorPack` (private VA `0x1ce74`) and
  `FileDescriptorUnpack` (`0x211fc`) were executed, with pinned instruction
  checks. No service factory, display initialization or commit was called.
- Negative FD roundtrip, unknown-number rejection, truncated-word failure,
  positive generated-number pairing, a distinct duplicated live FD, repeated
  unpack aliasing, real pipe data after vector release, and the nonduplicating
  path returning the caller FD all matched expectations.
- The original packer's strong reference was released with the original
  `RefBase::DecStrongRef`, using the actual virtual-base adjustment. The original
  unpacker itself copied/released its temporary side vector. No replacement
  parcelable or mock response was used.

## Scope

The vector, packer and unpacker are private hash-pinned layout witnesses, not
official headers or a stable public ABI. The one-element side vector was
preallocated, so growth/reallocation was not tested. This is **same-process**
command-word/FD-array matching: no Binder marshalling, cross-process HDI transfer,
SharedMemQueue exchange, composer request execution or desktop is established.
Repeated unpack returns the same FD number, not a second independently owned FD;
the probe closes the moved FD only once.

## Evidence / preservation

- Package: `reports/composer-fdstream-package-001/manifest.json`.
- Trial: `reports/composer-fdstream-run-001/`.
- Independent check: `reports/composer-fdstream-001-independent-verification.json`.
- Initrd SHA-256: `07c217a9b15e4b082e5cbb393a01d4203bdb62880bda8d33559ca907e4da51c4`.
- Serial SHA-256: `70a0a4189fa3bf3b3e931b0e02b291bf60a034171a4c76a7048e7b49b7833bd3`.
- All 295 parent archive records other than the private probe were preserved.
- All 378 prior native raw logs and four local/remote trial artifacts verified.
- Ubuntu boot ID, kernel and 13 loader configs unchanged; persistent Ubuntu
  default retained, no one-shot; screen timer enabled/active, logical screen off
  with no setter. Physical screen not observed.

## Next

Characterize original SharedMemQueue construction/read/write and its actual
ashmem prerequisite before attempting full composer request/reply. Keep the
same no-device isolation and do not substitute fake shared-memory success.
