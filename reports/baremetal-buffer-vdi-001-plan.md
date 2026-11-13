# Private render-only buffer VDI probe

This is a bounded graphics-contract experiment, not an installed HDI service or a HarmonyOS desktop.

## Evidence and design

- The verified native trial 008 already covers FD690 rendering, DMA-BUF import and native fences using OHOS Mesa003. Its artifacts and logs remain unchanged.
- The HarmonyMac reference uses primary-node dumb allocation. A generated private copy instead selects only the genuine MSM render node `226:128`, using GBM linear buffers. It cannot call the reference primary-node selector or set DRM master.
- Current original SDK `libbuffer_handle.z.so` is hash-pinned to `9c3ab7c3c83e074d0238814153752656c28b56202f833ad07f34b2cffd640912`. The old experimental SDK copy is not substituted. The fixed header is 56 bytes, with reserve counts at offsets 48 and 52.
- Original SDK dependencies are copied from the previously verified original IPC bundle, while Mesa003, its GBM backend, the original OHOS loader, libdrm and NDK C++ runtime are copied from the verified fence bundle. Original SDK C++ and NDK C++ are distinct libraries; their coexistence needs runtime validation, not an assumption of ABI equivalence.

## Probe requirements

1. Invoke the actual original SDK `AllocateBufferHandle(2,3)` and verify counts, main/reserved FD initialization and the header ABI before invoking the VDI factory.
2. Allocate only independent RGBA buffers: odd geometry `13×7`, then panel-sized `1600×2560`.
3. Check CPU-to-GPU coherence through the VDI shadow mapping/flush and real EGL DMA-BUF import/readback.
4. Keep the CPU mapping live, clear the imported buffer on the GPU, finish GPU work, invalidate the CPU cache and require exact CPU-visible RGBA `191,64,128,255`.
5. Destroy only these buffers and private test resources. No KMS, window creation, input access, native token assignment or original system-library replacement.

The render-node admission C test was observed failing before implementation and then passed: wrong device type, primary node, wrong major/minor and null metadata are rejected. These are CPU metadata checks, not GPU proof.

## Current status

Candidate 004 passed strict compilation, runtime dependency closure and the actual original SDK factory test. On the MateBook's Ubuntu kernel, both geometries passed CPU-to-GPU and GPU-to-CPU exact pixel checks using FD690. The independent verifier checked all 34 archive and deployed files, live render-only sandbox policy, unchanged boot/default entries and already-off GNOME state. See `baremetal-buffer-vdi-run-004/independent-verification.json`. This is not yet a native-kernel allocator test.

Earlier failed packages remain unchanged: 001 exposed reference default-method unused parameters and a format mismatch; 002 exposed missing unversioned development linker names; 003 exposed an unused unrelated pixel-policy helper. Candidate 004 uses explicit versioned SONAME linking, the corrected format and only the renderer admission helper. No original reference or SDK file was edited, and no general warning suppression or runtime permission exception was added.

The adapter retains reference bounds and metadata behavior. This first probe does **not** establish all format/usage combinations, cross-process handle serialization, compositor integration or synchronization without `glFinish`. Reference files are read-only inputs; only HarmonyMac has been identified from the two user-provided reference projects so far.
