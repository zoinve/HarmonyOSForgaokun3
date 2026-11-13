# Native trial008: Mesa FD comparison fix verified

Candidate011 passed the unchanged OHOS fence executable on native kernel `7.1.0-rc3-gaokun3-el2` and returned to Ubuntu. The previous FD identity warning is absent. Only five Mesa library records changed relative to candidate010; executable, loader, libdrm, C++ runtime, launcher, diagnostic init/helper, native kernel, DTB and modules were unchanged. The functional build change was explicit `allow-kcmp=enabled`.

## Actual results

- All 13 explicit module requests, storage, identity, DRM observation, enumeration, GPU and kernel-log phases returned zero.
- Binder protocol 8 / features 5; legacy device; active SELinux initial enforcing=1; own task tokens zero; no identity/permission writes and no policy loaded by the probe.
- DRM nodes card0/renderD128 exist; DSI-1 is connected with 1600×2560 modes, DP connectors disconnected; Himax input2/event2 registered. These do not prove physical scanout or touch interaction.
- Actual private sandbox: UID/GID 65534, groups/capabilities zero, no-new-privileges, private PID/mount/network namespaces and no primary DRM node.
- FD690 / EGL 1.5 Mesa Project / OpenGL ES 3.2 Mesa 25.0.1 / GBM DRM. Linear 16×16 buffer: stride 256, offset/modifier 0.
- Native fence polls readable and reimports with wait `0x30f6`, status `0x30f2`.
- GPU readback and second independent GBM-device DMA-BUF import/map both return opaque red center `(255,0,0,255)` and blue background `(0,0,255,255)`.
- `FENCE001_PASS`, launcher exit 0 and GPU phase 0. No FD identity warning or fence/launcher failure marker. Overall end explicitly retains `desktop_verified=0`.

## Independent evidence

All **264** raw files passed size/SHA-256 checks: 226 historical files plus 38 new **cumulative snapshots**, not 38 independent tests. Final snapshot:

`native-diag-001-21d0af40-d9df-4cf3-84f3-bdbbbbbed6c0/phase-038.log`

81,990 bytes; SHA-256 `5b6d79c8a318fc06c7e5be2c20710e4665ba5e0cbd72206ec330b10026834c26`. Device-tree model NUL is preserved.

See `baremetal-native-trial-008-mesa-verification.json`, `baremetal-native-trial-008-independent-verification.json` and the immutable collected raw logs. The archive's independent comparison proves only the five Mesa records changed; no new GPU run is inferred from package checks.

## Return and preservation

Ubuntu `7.1.0-rc3-gaokun3+` returned with boot ID `7d801586-cb86-4983-ab3f-5e3f249b01df` (previous `6c8229ac-31cf-4ac6-9de7-3794b3f7d1eb`). First SSH probe began after ~1.3 microseconds; 21 probes observed Ubuntu at 63.30 seconds. This is observation latency, not exact boot duration.

Ubuntu remains default, no one-shot remains, screen-off timer/service succeeded and GDM was already logically off. The verifier refused all display setters; physical screen state was not observed. The collector left the lab filesystem read-only.

Only tracked old EFI change across reboot: `loader/random-seed`, `935fa1731563a8798efd49948c3517117294e245b12dbd44a9f30542bd1bc4dc` → `c9d9bddccc7d0e371aeede3ab6fa14465852d9ba2fd7e9406f5cf2de99f8327d`. Fresh entropy was not restored to an old value.

Cleanup005 archived the consumed `harmony-native-diag-011+0-1.conf` locally and in `/var/lib/harmony-lab-boot-entry-cleanup-005`, then removed only it (SHA-256 `0e6cc410aebe9190e6cdb3763fee3e8bc1befa88c495e8381bff2a091ec12fa3`). All 82 other EFI files, defaults, assets and raw logs were preserved. Future installations need fresh post-cleanup baselines; do not rerun installer/trial008.

## Scope and next boundary

This verifies the exercised native offscreen GPU transport without the old FD fallback, not all descriptor-identity cases or stress stability. It does **not** verify a HarmonyOS desktop, native original service graph, physical display/input, or GPU authorization after loading a SELinux policy. Separate QEMU original-init/SAMGR evidence must not be conflated with this no-loaded-policy diagnostic.

Next investigate OHOS allocator/composer and display-service contracts without copying another process's identity or bypassing legitimate SA-query denials. HarmonyMac is confirmed as a reference; the second user-supplied project remains unidentified in the restored record.
