# Original composer parser: isolated characterization 002

## Outcome

- Original SDK service code executed successfully in a diskless, headless ARM64
  QEMU guest with **TCG**, not native hardware or KVM. Eight header cases matched
  their expected results; guest child exited normally with status zero.
- No service factory, InitDisplay, Commit, primary DRM node, physical GPU,
  guest network, disk, host filesystem share or host reboot was used.
- Independent verification checked local/remote serial, stderr, runner and result
  hashes; rechecked all 378 previous native raw files; and compared the package
  with its historical parent. Only `gpu-userspace-probe` changed; all other 295
  archived records, including the original service and init, were preserved.

## Evidence

- Package: `reports/composer-parser-package-001/manifest.json`.
- Successful trial: `reports/composer-parser-run-002/result.json`, `serial.log`.
- Independent check: `reports/composer-parser-002-independent-verification.json`.
- Initrd SHA-256:
  `70c3449caa4ac91f58c16e943a227ab1e2f6b32d9cad7556640d0f6386640114`.
- Original service SHA-256:
  `c5f7b2430aac4bee8edbeaea707805c0d9f33f6ee762a4a1f82452be01f92aab`.
- Serial SHA-256:
  `fc1ff18de1710dd5effe22912ae3df5744bd6ea4a405fee75e1619b0176d5157`.
- Runtime ~18.26 seconds; QEMU rc0, no timeout, child64 status0.

## Findings and limits

This is a private, hash-pinned binary experiment. The embedded mini-debug symbol
identifies `CommandDataUnpacker::BeginSection(int&)` at service VA `0x1ac38`.
The probe verifies its first four instructions before calling it through an opaque
state layout derived from this exact binary. The exported factory is resolved
only to obtain the ELF load base; it is never called. This does **not** establish
a stable public ABI, full HDI compatibility or service construction.

The 12-byte header is magic `0xb5b5b5b5`, signed command, then section length.
The test confirms acceptance of a valid `0x41` header; rejection of empty,
4-byte, 8-byte, 11-byte and incorrect-magic inputs; and the observed cursor and
command updates on failure. Importantly, **BeginSection alone accepts length0
and length0xffffffff**. No payload is followed in these two cases. This is not
evidence that the complete parser accepts them, nor evidence of a vulnerability:
subsequent section/payload validation still needs investigation.

An independent original-ELF PT_LOAD lookup confirms jump-table byte20 at
`0x62f2 + (0x41 - 0x40)`, leading to thunk `0x1c884` and the actual call to
`OnSetDisplayClientBuffer` at `0x1df00`. Dispatcher zero return is not sufficient
to prove handler success because handler return values are discarded there.

Static FD analysis (not runtime verified): the original client writes negative
FDs directly as signed command words. For nonnegative descriptors it creates a
numbered HdifdParcelable object, appends a 16-byte HdifdInfo to the side vector,
and writes the generated number into the command stream. Service unpacking
matches this number against side-vector entries and calls HdifdParcelable::Move;
negative words yield output-1 and success, and unmatched nonnegative numbers
yield failure/output-1. Fence packing's bool selects a different parcelable
construction/Init path. Descriptor duplication, closure, marshalling and actual
SMQ transport still require direct runtime evidence; none are claimed here.

The isolated guest has no HiLog daemon: original logging reports connection
errno2 repeatedly. Those messages are preserved rather than suppressed or stubbed.
HiLog/service-manager startup is not tested by this probe.

## Host preservation and failed attempt

Trial001 stopped before guest execution: current Ubuntu has no `/dev/kvm`, and
QEMU returned1 while initializing KVM. Its failure records remain intact; it was
not rerun. Trial002 changed only the acceleration/CPU choice to software TCG /
cortex-a72, without loading modules, installing software or changing boot state.

Ubuntu boot ID remained `6b46894a-8b4b-49a4-bf71-5a903d6b3d95`, kernel
`7.1.0-rc3-gaokun3+`. All 13 loader configuration hashes were unchanged; persistent
Ubuntu default and absent one-shot were independently checked. Screen-off timer
remained enabled/active; an independent read-only check found greeter logical
screen state off and changed=false. Physical screen was not observed.

## Next boundary

Characterize original FD parcelable ownership and client packer in the same
no-device guest, then the actual SharedMemQueue exchange/error reply path. Do not
promote this parser-only result to complete SMQ, original composer-service,
RenderService, physical scanout or HarmonyOS desktop verification.
