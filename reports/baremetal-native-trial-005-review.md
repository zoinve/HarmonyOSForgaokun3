# Trial 005: identity kernel on the MateBook

**The native patched kernel passed the non-mutating ABI helper and retained DRM/input enumeration. This is not a HarmonyOS boot or desktop result.**

The single-attempt 008 diagnostic returned to Ubuntu `7.1.0-rc3-gaokun3+`, boot ID `89d65d38-a2e5-45da-88f1-8affc0696d8a`, replacing prior Ubuntu boot `7a8e898d-2e89-4f99-b476-14e66d3c44f2`. SSH observation started approximately 1.5 microseconds after entering the observer, with no initial fixed delay. Fourteen probes observed the returned boot at approximately 57.448 seconds; this is observer latency, not an exact boot-duration measurement.

## Verified raw evidence

All **152** collected raw files passed independent byte-count and SHA-256 checks. Of these, 116 are prior evidence and 36 are new cumulative snapshots, **not 36 independent tests**. The new diagnostic boot is `native-diag-001-0f3bb398-fc28-43c8-b2fb-606f0c7ab892`, ending at `phase-036.log`. Raw logs retain the device-tree model's NUL byte unchanged.

- `native-identity-read`: status 0, `NATIVE_IDENTITY_READ001_PASS protocol=8 features=5`, initial task self/first identities both zero, `tokens_modified=0 permissions_modified=0`. The helper also checks honest unsupported-command errors and fresh Binder identity/reserved bytes, then removes its RAM-only binderfs instance. This does not exercise board-side transactions.
- Storage and all 13 explicit module requests returned 0. The existing UCSI/HPD/DP, DPU, DSI, clock and PHY chain bound; the Adreno driver bound. DRM observation and enumeration returned 0.
- `/dev/dri/card0` and `renderD128` exist; DSI-1 is connected and reports `1600x2560`; DP-1/2 are disconnected. Kernel DRM initialization is logged at 1.227853 seconds and GMU firmware loading at 1.228577 seconds.
- Himax remains registered as `input2` / `event2`. This is input registration, not a physical-touch event/calibration test.
- The final marker remains `NATIVE_DIAGNOSTIC_END desktop_verified=0`. No actual scanout, rendering under this patched kernel, native OHOS userspace, complete token services or HarmonyOS desktop was tested in this trial.

The intentional unsupported command 25 logs an access-token command error; this corresponds to the helper's required error test, not a fabricated implementation. Existing EC/PHY and DSI device-link warnings remain visible despite successful DRM enumeration; do not silently describe the kernel log as warning-free. Standalone GMU and EC battery child driver links are absent, as already observed separately; no readiness claim relies on them.

## Return and preservation

The consumed entry is `harmony-native-diag-008+0-1.conf`. Installer-time preservation covered all 70 pre-existing EFI files. Across the boot, the only tracked pre-existing EFI change was `loader/random-seed`, from `9f9f89e6602a7c7a36825c65ae29e34135e2c5755fb88cf407df596688ebb750` to `4f93ddd2b7f53bf7be71c4c20b8e546d8f98d569710e691ff4f8e19bcc25c6ba`. Do not restore the stale seed or claim all EFI bytes were unchanged after boot. The collector mounted the isolated lab filesystem read-only.

Independent post-return verification confirmed the persistent Ubuntu default, absent one-shot and successful enabled/active screen-off timer. The active GDM greeter already reported logical screen-off; the verifier explicitly rejects every display setter and did not change that state. Physical panel-off was not observed. The consumed config is eligible for separately archived, guarded cleanup under the user's existing request; retain kernels/initramfs assets and all raw evidence.

Reports: `baremetal-native-trial-005-evidence`, `baremetal-native-trial-005-collected/collection.json`, and `baremetal-native-trial-005-independent-verification.json`. The original SDK APIs, raw synchronous/one-way/nested transactions and Connector negotiation have separate QEMU evidence; their coverage must not be presented as additional board tests.
