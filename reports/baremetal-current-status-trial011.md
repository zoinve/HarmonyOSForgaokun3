# Current status after native trial011

- Native profile003: Binder/token read-only ABI, DRM display enumeration and touchscreen registration verified; initial SELinux enforcing is active, but the diagnostic does not load a policy.
- Native GPU: OHOS Mesa hardware drawing, native fences and independent GBM mapping verified in trial008.
- Native allocator: original SDK BufferHandle ABI and CPU↔GPU coherence verified in trial010, with `glFinish` as the scoped synchronization mechanism.
- Native cross-process graphics: trial011 now verifies separate-exec DMA-BUF/fence transfer, descriptor ownership and exact pixels on FD690. See `baremetal-native-trial-011-review.md`.
- Separate QEMU evidence: genuine original SDK init boots using its own developer policy; genuine SAMGR ping and authentic native reply identity are verified. Privileged queries from the zero-token observer are legitimately rejected, not bypassed.

**Not completed:** integrated native HarmonyOS init/service boot, HDI composer integration, physical desktop scanout, actual touch events, or a usable HarmonyOS desktop. Separate evidence scopes must not be merged into a claim of system readiness.

Ubuntu, its persistent default and automatic logical screen-off remain preserved. Original SDK images and historical evidence remain retained. HarmonyMac is the confirmed reference project; the second user-provided reference is still not identified in the restored records.

Next: compare actual composer buffer/fence interfaces with the verified private transport, then build a bounded offscreen interface test without changing display state or identities.
