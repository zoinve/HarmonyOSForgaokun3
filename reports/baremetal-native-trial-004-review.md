# Native trial004 / candidate007

## Verified outcome

The sole generated-C change from candidate006 was the explicit `ucsi_huawei_gaokun` request after EC. In this native run the previously missing bridge chain bound and DRM initialization completed:

- UCSI child, both HPD bridges and both auxiliary bridges have actual driver links.
- Both DP controllers bound; kernel component logs also show both DSI controllers and the GPU bound to the DRM master.
- Kernel: `[drm] Initialized msm` at uptime1.202052; GMU firmware loaded at1.202492; msmdrmfb framebuffer registered at1.544574.
- The unchanged condition-based observation returned0 with `DRM_NODE_OBSERVED_NOT_DISPLAY_PROOF`; the final binding snapshot was at uptime1.64seconds.
- `/dev/dri/card0` and `renderD128` exist. DSI-1 reports `connected`, with 1600x2560 modes; DP-1/DP-2 report `disconnected`.
- Himax touchscreen remains registered at input2/event2. Enumeration returned0.

All13 explicit module requests (including PCIe PHY and NVMe) returned0. Lab storage returned0. These observations support the missing UCSI/HPD supplier explanation for the previous no-DRM result; they do not establish physical touch events, visible panel scanout, stable GPU rendering, or HarmonyOS integration. Existing device-link warnings remain in the raw kernel log. Final `desktop_verified=0` is not promoted to success.

## Return and evidence integrity

The authorized soft reboot request returned0. Immediate SSH observation started at0.0000011seconds, used19 attempts, and confirmed changed Ubuntu boot ID at observation time61.7980849seconds; this is not an exact boot-duration measurement.

- Before Ubuntu boot: `151d2ca0-706f-4eb9-8edc-f1b0f9093a3d`.
- Diagnostic boot: `66056fef-c7cb-4619-beea-32be6b7f7fc3`.
- Returned Ubuntu: `7a8e898d-2e89-4f99-b476-14e66d3c44f2`, kernel `7.1.0-rc3-gaokun3+`.
- Independently verified all116 collected files by byte length and SHA-256. There are34 new cumulative snapshots, not34 independent tests. Final raw file: `baremetal-native-trial-004-collected/native-diag-001-66056fef-c7cb-4619-beea-32be6b7f7fc3/phase-034.log`.
- The only tracked preexisting EFI-file change across boot was `loader/random-seed`, SHA-256 `1114e653096981e845d0d2474af867a894ada82a853f06fa90c3d5cc7c0de327` to `9f9f89e6602a7c7a36825c65ae29e34135e2c5755fb88cf407df596688ebb750`. It was preserved, not restored.
- Collector mounted the lab read-only. A successful return does not prove recovery from a future kernel hard lock or a successful final diagnostic unmount.

Read-only post-reboot screen verification in `ubuntu-screen-off-001-post-trial-004.json` found the timer enabled/active, service result success/exit0, and the active GDM session already off. The verifier forbade display setters. This is a logical compositor-state observation, not a physical panel observation. Ubuntu remains the persistent default and no one-shot remains selected.

## Authorized stale-entry cleanup

After collection, the user's cleanup request was applied only to the four consumed entries004–007. See `boot-entry-cleanup-001.json` and `boot-entry-cleanup-001-notes.md`. No previous trial evidence was rewritten. Future trials must take a fresh baseline; older preservation scripts intentionally assume pre-cleanup entry files and must not be rerun.

## Remaining milestone

Native Linux storage, DRM connector enumeration and touchscreen registration now have direct evidence. Genuine native HarmonyOS still requires its kernel extensions, native graphics/userspace adaptation, event delivery and a verified desktop. Do not describe this Linux diagnostic as HarmonyOS boot success.
