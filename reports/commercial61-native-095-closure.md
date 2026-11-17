# Native 095: genuine UDID available; normal close leaves OOBE focused

## Execution And Preservation

Exactly one boot from 2026-11-15 09:25:20.975865 to 09:29:05.586448 UTC.
Run `commercial61-native-087-2d4f08ba-3193-4dd1-8afd-3ff0801403f9`.
The final cumulative phase contains the bounded timeout, target exit PID 437
status 9, `NATIVE_ORIGINAL_END` and `NATIVE_DIAGNOSTIC_END`. This was not the
incomplete 094 user-interrupted evidence pattern. Ubuntu returned with boot ID
`c99b2934-bea9-49ac-be31-979e88ac3d0a`.

131 recovered file hashes match. The physical-serial and original-UDID export
guards passed; LAB was read-only/noload and is unmounted. The Wi-Fi secrecy
check passed over 384,898,436 bytes without exporting the credential. Its first
attempt failed on WSL/Windows SSH path handling; the corrected local transport
completed without another boot.

Post-return verification confirms Ubuntu current/default, enabled/active display
timer, original manual entry, unchanged firmware and four original images.
154 prior EFI files remain unchanged except normal loader random seed and the
hash-archived removal of entry 092. Entries 094/095 and all shared payloads remain.

## Identity Progress

The unchanged early093 wrapper succeeded and unmounted its temporary genuine
sysfs mount. Original init consumed matching physical model and boot serial.
Before the late helper requested any action:

- `ohos.boot.sn`: length 16, matching physical firmware.
- Manufacturer and model: length 6 each, matching physical firmware.
- `const.product.devUdid`: length 64.
- Original `GetDevUdid`: return 0, length 64, valid hexadecimal.
- Helper decision 0 and exit 0: no late identity write or module load requested.

The identity was produced by the original initialization path, not a replacement
algorithm or borrowed model/serial. Raw identities were not exported. This is
identity availability, not certificate provisioning or commercial activation.
Recovered DCM logs contain zero `GetDevUdidData ... Failed` lines, in contrast to
092; the direct original API result is the stronger availability evidence.

## Normal Close Result

At the guarded request, original WMS focus was guide window 8, PID 6401. The
verified physical keyboard `/dev/input/event6` accepted the one Alt+F4 chord.
Original SceneBoard PID 4578 logs `usual.event.ALT_F4` at target time 17:27:55.308,
with `isOobeEnable: true`, unlocked and no Ctrl+Alt+Del panel.

Nevertheless at both monotonic 130 and 140 seconds, original WMS still lists the
same guide PID/window as focus 8. No successful normal window dismissal is
established. This is distinct from the previously disproven repeated force-stop
approach. Do not repeat this completed close request or disable OOBE policy.

## Pixels And Remaining Activation Failure

Both full-resolution captures are complete at source 2560x1600/output 1600x2560,
with zero clockwise rotation differences. Capture times are 120.026949 and
140.001975 seconds; 1,378 source pixels differ. OCR of both source frames reads
the guide's device-identifier/activation-rights notice. Image inputs remain
unavailable to the viewer; OCR and pixel changes do not prove a desktop or a
visible desktop interaction.

Original DCM still records `TEEC initial failed ffff0000` in 26 matching log lines
(including repeated error-chain summaries, not 26 distinct attempts). This is
independent of the now-successful original UDID result. Native TA certificate
queries/attestation remain unsuccessful. No server rejection or absence of a
hardware certificate is proven by the failed local TEE initialization.

## Next Work

Keep the verified early hardware/original identity path. Investigate genuine
compatibility of the original `/dev/tc_ns_client` and `/dev/tc_private` clients
with this hardware/kernel/secure firmware, or a supported original guide exit
flow. No fabricated certificate, identity, provisioning state or success API.
Desktop visibility, persistent interactive use and commercial activation remain
unproven. Do not boot 095 again.

Evidence: `hardware-runtime-analysis.json`, `normal-close-runtime-analysis.json`,
`network-refresh-runtime-analysis.json`, `full-frame-analysis.json`,
`second-full-frame-analysis.json`, `post-return-review.json`, retrieval manifest
and the separate post-return preservation audit under this experiment's reports.
