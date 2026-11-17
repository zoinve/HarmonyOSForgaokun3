# Basic Driver Integration 001

## Goal Switch

On 2026-11-16 the user confirmed desktop entry and switched the active objective to basic drivers. Stop OOBE/activation experiments. User confirmation is distinct from automated acceptance: experiment 124 independently established original SettingsData values of one, OOBE disabled, no observed guide launches/recovery, original lockscreen rendering and keyboard delivery. Its two full-resolution frames were identical; visible desktop interaction was not independently verified by that run.

Preserve the working baseline, original images, Ubuntu default, manual entry, firmware, screen-off timer and numbered evidence. Experimental entry files currently retained: 123 and 124. Both payloads and private setup seed remain intact. There was no reboot after the goal switch.

## Read-Only Inventory

Evidence: `basic-driver-baseline-001-20261116T012519794664Z/result.json`. This is Ubuntu/kernel context, not HarmonyOS service acceptance.

| Area | Real hardware exposed by the shared kernel | Integration work |
| --- | --- | --- |
| Display/backlight | DRM panel; `ae96000.dsi.0`, maximum brightness 4095 | Preserve working composer; connect actual brightness to original service ABI |
| Input | Himax touchscreen; USB 12d1:10b8 keyboard/touchpad; lid and power-key events | Verify coordinate alignment, clicks, scrolling, gestures and hotplug through MMI |
| Wi-Fi | `ath11k_pci`, carrier up in Ubuntu | Validate existing genuine supplicant bridge and native NetManager supplier/IP/DNS |
| Bluetooth | `hci0`, `hci_uart_qca` | Match vendor HCI transport ABI and controller ownership; test discovery/pairing |
| Audio | SC8280XP-HUAWEI-GAOKUN3 ALSA card; two playback and two capture PCMs | Board-specific routing/UCM/firmware and Audio VDI/HDI; do not copy L410 TAS amplifier setup |
| Battery/charging | `gaokun-ec-battery`, EC adapter and two UCSI supplies | Map measured fields, optional values and plug events into original service |
| USB/power | xHCI hubs, HID and EC/UCSI; lid and power-key inputs | Verify port hotplug, charging, suspend/resume after basic functionality |

References reviewed: L410 adaptation backlight, battery, audio and Bluetooth sources; Linux compatibility platform source inventory and ALSA configuration entry point; HarmonyMac's pinned setup method remains the preserved desktop baseline. Reference hardware paths and binary ABIs are not portable assumptions.

## Implemented Backend

`next-experiment/gaokun-basic-sysfs-001.c` and its header provide a small C hardware access layer, not an invented HDI implementation:

- Reads real battery presence, percentage, charging state, microvolts, signed microamps and optional deci-Celsius temperature. Validity flags distinguish absent/invalid data from a genuine zero. It does not fabricate temperature, health or charging state.
- Reads/scales brightness between the actual maximum and 0-255; writes only an existing brightness attribute. It rejects invalid levels, malformed/overflowed numbers, absent files and short/error writes.
- No hard-coded L410 sysfs node, fake service state, authentication change, permission bypass or automatic device mutation.

Six temporary-fixture tests passed, including malformed/missing values, signed current, exact scaling, overflow and refusing to create a missing attribute. Strict native and AArch64 builds passed with `-Wall -Wextra -Werror`.

Live read-only evidence: `gaokun-basic-sysfs-live-001-20261116T012832914944Z/result.json`. The cross-built backend loaded on the actual ARM64 host and read 98%, Full, 8298000 microvolts, zero microamps and brightness 13/255. Temperature was unavailable (`valid=31`, temperature bit clear); the zero-initialized storage is not a measured zero temperature. The brightness setter was not called. Temporary target files were removed.

## Next Boundary

Match original battery/backlight library symbols, service configuration and data layout before wiring this backend into a separate reversible RAM overlay. Keep power management behavior unchanged until readings and UI controls work. Next prioritize native input/network acceptance and board-specific audio/Bluetooth transport. Do not claim these complete from Ubuntu enumeration or backend unit tests.
