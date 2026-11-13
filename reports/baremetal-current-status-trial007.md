# Current status after native trial007

Historical snapshot. Current native Mesa003 regression and preservation results are in `baremetal-current-status-trial008.md` and `baremetal-native-trial-008-review.md`; the pending native regression discussed below has now passed without the FD warning.

## Verified milestones — keep scopes separate

- **Native board hardware/ABI:** native profile003 booted with legacy Binder protocol8/features5 and active SELinux initial enforcing1. DRM exposed a connected 1600x2560 DSI connector and Himax input registration. Diagnostic probes did not load a policy or modify identities.
- **Native board GPU + OHOS userspace:** trial007 ran the unchanged OHOS Mesa Freedreno bundle on our own native kernel. FD690 shader pixel readback, native fence export/wait/reimport, and a second GBM-device DMA-BUF import/CPU pixel readback passed in an unprivileged render-node-only sandbox. This is no longer only Ubuntu-kernel GPU evidence.
- **Original SDK IPC:** isolated earlier QEMU tests passed original token APIs, genuine SDK transactions, nested callback dispatch and caller-context restoration. Those early IPC tests had no active SELinux and are not retroactively enforcing-policy results.
- **Original SDK init under enforcing SELinux:** separate QEMU boots of read-only original images plus fresh disposable data reached genuine SAMGR and registrations. Original manager PING and authentic native-type-1 reply-sender metadata passed under the SDK-selected developer policy. This is distinct from separate production-policy tests and from full-system readiness.

## Not verified / not bypassed

No usable bare-metal HarmonyOS desktop, complete native service graph, physical scanout/touch interaction or loaded-policy GPU authorization is claimed. Privileged SA List/Check correctly rejected the pre-init observer's actual zero-token identity; no identity copying, invented native tokens, substitute manager or policy exception was introduced.

The Mesa FD-identity fallback was traced to build configuration: `auto_features=disabled` left `allow-kcmp=auto` disabled. The old compiled function returned -1 without invoking kcmp or setting errno. Mesa003 explicitly enables `allow-kcmp`; its real comparator passed duplicate/independent descriptor tests. Reusing the exact old fence executable with only five updated Mesa libraries also passed FD690 pixels, DMA-BUF and native fence tests on the Ubuntu kernel, with the warning absent. Independent build verification covered all 34 artifacts. This does not yet supersede trial007's own-native-kernel result: the new libraries still need native-sandbox regression. See `baremetal-mesa-fd-identity-001-review.md`.

## Preservation

Trial007 returned Ubuntu `7.1.0-rc3-gaokun3+`, boot ID `6c8229ac-31cf-4ac6-9de7-3794b3f7d1eb`. All 226 raw files passed size/hash checks. Ubuntu remains default; the enabled screen-off timer and already-off logical GDM state were independently verified without setters. No physical screen observation is claimed.

The consumed010 loader configuration was archived locally and remotely, then removed alone; all 79 other EFI files remained byte-identical during cleanup. Assets, original images and raw logs were retained. Reboot rotated the tracked random seed: preserve the new seed. All future diagnostics need fresh numbers and a fresh post-cleanup EFI baseline.

HarmonyMac is the confirmed reference project; the second user-supplied reference remains unidentified in the restored record, not silently replaced by another project.
