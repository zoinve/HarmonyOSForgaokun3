# Current status after 046

Historical checkpoint: the newer board/GPU status is in `baremetal-current-status-trial007.md`. The native-kernel preparation described below has since been tested in trials006 and007.

## Verified, with separate scopes

- **MateBook native diagnostic:** the identity-candidate kernel passed read-only Binder/token checks, retained DRM card/render nodes, a connected 1600×2560 DSI connector, and registered Himax input. This was not a HarmonyOS desktop or physical touch/scanout test.
- **Original OHOS graphics runtime on Ubuntu:** Freedreno FD690 rendered and returned exact pixels; linear DMA-BUF export/import, a second GBM-device CPU readback, and native-fence synchronization passed. These were offscreen render-node tests, not native HarmonyOS graphics integration.
- **Original SDK IPC in isolated QEMU:** original token APIs, Binder connector, request/reply, genuine SDK nested callback dispatch, and caller-context restoration passed. Early IPC-only tests had no active SELinux and are not retroactively claimed as enforcing tests.
- **Original SDK init boot with enforcing SELinux:** unchanged original images attached read-only and a fresh private scratch data filesystem reached genuine SAMGR and service registration. A genuine manager PING passed. In 046, the same fd returned actual UID-5555/PID-83 sender metadata with nonzero native-type-1 token, zero first token and reserved fields, and no identity changes. Independent 046 verification passed.

## Intentionally not bypassed

The pre-init observer has actual token zero. Original privileged List/Check queries rejected it; those errors are not empty results, missing services, or a reason to copy another process's identity. No token/SID/policy workaround was introduced. SDK-selected developer policy and separate production-policy conformance tests remain distinct.

## Next native preparation

An inert native profile-003 kernel/module package has been generated, separately from the QEMU-only storage kernel. Independent byte verification passed for the archive, all 391 modules, kernel, DTB, and native configuration. It still needs a fresh, scoped diagnostic init and preservation/recovery checks before any board trial. Full native HarmonyOS userspace, the complete service graph, display integration, and a usable desktop remain unverified.

Ubuntu remains the persistent boot default; its automatic screen-off timer is retained. Current work has not rebooted the MateBook or modified original SDK images. Existing one-shot diagnostics and raw evidence remain immutable; later trials must use fresh numbers and a fresh post-cleanup EFI baseline.
