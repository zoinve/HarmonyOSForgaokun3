# Basic Driver Integration 003

Date: 2026-11-16. Goal remains all native basic drivers, not only battery or
backlight. OOBE/activation work remains stopped. User-confirmed desktop and its
unchanged original seed/runtime remain the baseline.

| Area | Verified This Stage | Still Required |
| --- | --- | --- |
| Backlight | Original RenderService request 11363; real brightness/actual_brightness 512 to 710, max 4095 | UI slider/physical luminance, range and sleep transitions |
| Battery | Real EC bound; original Battery HDI/powermgr consumes measured 98%, present, voltage/current, Full and USB online state | Plug/unplug transition, UI acceptance, no invented missing temperature/health |
| Keyboard/input | Original SceneBoard receives keyboard events; display rotation preserved | Physical touch/touchpad coordinates, click/scroll/gestures, hotplug |
| Wi-Fi | Existing genuine supplicant bridge and prior guest DHCP evidence preserved | Native NetManager supplier/IP/DNS and user-facing connectivity acceptance |
| Audio | Real Ubuntu board/ADSP bindings mapped; exact native modules and firmware verified as packaged | Native module/DSP/ALSA bring-up, board routing, original audio HDI, playback/capture |
| Bluetooth | Real hci_uart_qca binding mapped; exact UART/controller modules packaged | Native controller initialization, transport ownership, discovery/pairing |
| USB/power | Existing HID and EC/UCSI baseline preserved | USB hotplug, charger transitions, suspend/resume after basic drivers |

Operational 131 exposed a pre-service seed-copy timeout but verified genuine
kernel battery readings. Its early logs and failure are preserved. Operational
133 fixed that bounded copy limit and verified original battery-service data
plus real backlight readback. Both are completed experiments and MUST NOT be
rerun. See commercial61-native-131-closure.md and
commercial61-native-133-closure.md for hashes, exact evidence and limits.

Current Ubuntu boot ID: f11a4c53-00b4-4139-9b2d-aebf8c957c3f. Current experiments:
131/133; older entry contents/hashes are archived, shared payloads not deleted.
Original images/firmware, Ubuntu default/manual entry and active screen-off
timer passed checks after both boots. No required process session is pending.

Next work: explicit native audio/BT kernel initialization and read-only
sound-card/DSP/HCI acceptance, using reports/audio-bluetooth-payload-135/result.json
and reports/audio-bluetooth-inputs-134-20261116T023823269998Z/result.json.
Use modinfo dependencies from audit 135, not the original collector's
mislabelled reverse-user field. Preserve the original audio service and use
SC8280XP/WSA883x/WCD938x routing, not L410 TAS register sequences. An absent
module in exported early snapshots is not proof it never loaded later.
