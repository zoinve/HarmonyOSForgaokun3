# Private allocator 004: original handle ABI and GPU coherence

## Actual result

The unchanged original SDK BufferHandle library and the private render-only reference adaptation passed on the MateBook under Ubuntu `7.1.0-rc3-gaokun3+`:

- Actual `AllocateBufferHandle(2,3)`: 56-byte fixed header, reserve-count offset 48, initialized main/reserved FDs all `-1`.
- FD690 rendered through OHOS Mesa003, without primary-node access or KMS changes.
- `13×7`: stride 256, allocation size 1792 bytes.
- `1600×2560`: stride 6400, allocation size 16384000 bytes.
- Both samples: CPU fill and VDI flush produced GPU RGBA `64,128,191,255`; GPU clear plus `glFinish` and VDI invalidation produced CPU RGBA `191,64,128,255`.
- Probe exit 0, no new kernel log, no FD-identity warning. Allocation, unmapping and freeing completed.

The original SDK C++ runtime and the NDK C++ runtime coexisted for this limited path. This does not establish general ABI interchangeability. Missing HiLog-server messages and the reference's first-free process-map debug output are preserved in raw evidence.

## Isolation and independent verification

Both live transient-unit policies were captured before execution: unprivileged user, no capabilities, no-new-privileges, device policy closed except renderD128, private network and temporary files, strict read-only system, 45-second runtime and 512 MiB memory bounds. Admission opened the render node and rejected card0.

`baremetal-buffer-vdi-run-004/independent-verification.json` verifies all 34 archive and remote file sizes/hashes, the original SDK handle-library hash, exact result markers and live policies. Bundle archive SHA-256: `c8e920ccf777775986771d04b586afeffe995ca882869f9ae09b961c725ed084`.

Ubuntu's boot ID and persistent default remained unchanged; no pending one-shot or stale diagnostic entry exists. GNOME was already logically off; the verifier refused all screen setters. Physical darkness was not observed.

## Limits and next step

This is not an installed allocator service, native-kernel allocator regression, compositor, physical scanout, cross-process handle test or HarmonyOS desktop. Coherence currently depends on explicit `glFinish`; other formats and usage combinations remain unverified. Next, reuse this exact validated bundle in the existing bounded native diagnostic sandbox, keeping the kernel, init, launcher and identity helper unchanged.
