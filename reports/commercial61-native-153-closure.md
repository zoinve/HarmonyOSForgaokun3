# Native original libusb enumeration 153

Single completed boot: `commercial61-native-087-9eab4381-de39-4339-a4f0-55b6b5edff33`.
Returned to Ubuntu November 16, 2026 at 04:42:31 UTC.
All 188 retrieved evidence files matched remote hashes and were rehashed for analysis.

The added read-only helper loaded the image's original libusb and successfully
initialized and enumerated eight devices. Each bus/address matched the later
kernel snapshot: six root hubs, Huawei detachable HID 12d1:10b8 and Realtek
USB Ethernet 0bda:8153. The helper did not open devices, claim interfaces,
reset devices, change configuration or read serial strings.

Original MMI holds the touchscreen, and usb_storage/uas/exfat are live.
These observations do not prove physical touch accuracy, physical USB keyboard
input, original USB service acceptance, or storage file access. No USB storage
device was present among the eight enumerated devices.

Artifacts:

- `commercial61-native-153/native-usb-runtime-analysis-153.json`
- `commercial61-native-153/runtime-evidence/retrieval-manifest.json`
- `commercial61-native-153/runtime-evidence/raw/snapshot075-commercial-desktop086.log`
- `commercial61-native-153/post-return-verification.json`

Post-return verification passed: Ubuntu current/default; 175 prior EFI files
unchanged except the normal random seed; authorized old 148 entry archived/removed;
firmware and four original images unchanged; LAB unmounted; screen-off timer
enabled/active; original manual entry retained. Experimental entries 152/153 remain.

Settings failures captured in this run are analyzed separately in
`settings-diagnostics-155-findings.md`. They are not classified as a USB or touch failure.
