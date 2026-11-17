# Native Basic Driver Run 133

## Real Battery Service Data

The independently built EC module 132 registers the real battery as battery,
matching original Battery HDI 2.0 discovery. Its only source change is that
power-supply registration name. EC access, charging code, units, event handling,
original kernel image/config and original vendor HDI/service binaries remain
unchanged. Module SHA256:
11a4f35983142a36fdf51753643a72db05d09bc49702e58c70b3b439512101e4.

The real sysfs supply reports present=1, capacity=98, status=Full, current_now=0
and approximately 8.30 million microvolts. Original powermgr logs now publish
capacity=98, present=1, currNow=0, chargeState=3, pluggedType=2 and changing real
voltage readings, instead of run 130's mock capacity=11, present=0, currNow=1000
and fixed voltage=4123456. Original power_host logs access to the real sysfs
root, with explicit errors for absent optional attributes. No mock-path
creation log was found. Capacity, presence, current and voltage match the
independent kernel snapshots exactly in the supplemental service correlation.

The initial conservative analysis required an uncompressed path-success log
which the commercial image does not emit; it therefore retained a false
acceptance flag despite storing matching consumer records. Its output was NOT
overwritten. battery-service-correlation.json adds the separate four-field
comparison and real-provider-root evidence and passes its negative-case tests.

Temperature and health are absent from the real supply. The original service
sometimes publishes zero/default values for missing fields; these are NOT
measured temperature/health. No synthetic attribute was added. Physical plug
transitions, battery status UI and suspend/resume remain unverified.

## Real Backlight Readback

Before original services, brightness and actual_brightness were both 512 with
maximum 4095. Original RenderService requested logical level 11363/65535.
Subsequent independent snapshots read brightness=710 and actual_brightness=710,
matching the implemented rounded scaling. This verifies register readback
correlated to the original service request, not merely a removed error log.
The original composer/GPU pipeline was unchanged from run 130. Physical light
output and user-visible slider interaction are not independently verified.

## Runtime And Preservation

The unchanged seed passed its original hash checks with a 36-second copy probe
budget, fixing 131's 12-second timeout without changing seed contents or setup
flags. Original services launched. A full-resolution nonblack frame was
captured with exact clockwise scanout rotation; keyboard events reached
SceneBoard. Neither result independently proves desktop interaction. Desktop
entry remains user-confirmed acceptance, as required by AGENTS.md.

One boot only, from 2026-11-16T02:25:57Z to 02:30:04Z. Ubuntu returned with boot
ID f11a4c53-00b4-4139-9b2d-aebf8c957c3f. All 139 evidence files matched remote
hashes. Original hilog contains invalid UTF-8; analysis decodes with replacement
and records 91 replacement characters, while original bytes/hash remain intact.
Physical-serial/original-identity scans and exact private-PSK scanning passed.

Post-return checks passed: Ubuntu current/default, manual entry, enabled/active
screen-off timer, original firmware and four original images. 168 prior EFI
files are unchanged except normal random-seed change and the authorized,
hash-archived removal of experimental entry 130. Current experimental entries
are 131/133. Shared payloads, seed and working runtime remain intact. LAB was
read-only/noload during retrieval and is now unmounted.

## Next Driver Boundary

Read-only Ubuntu inventory 134 identifies snd_soc_sc8280xp, WSA883x/WCD938x,
the qcom_q6v5_pas ADSP path, and hci_uart_qca. Payload audit 135 verifies that
the needed modules and ADSP/SLPI/CDSP firmware already exist in the exact 133
initrd. Their loaded state was not observed in exported native module
snapshots; those snapshots do not prove absence at every later runtime instant.
Next add explicit bounded loading and native sound-card/DSP/HCI observation,
then original audio HDI and Bluetooth transport acceptance. Do not copy L410's
TAS amplifier setup or treat packaged firmware as successful native audio.

The first Ubuntu collector labelled /proc/modules' fourth field dependencies;
that field actually lists reverse users. Original inventory is retained;
audit 135 provides normalized used_by fields and actual direct dependencies
from modinfo on the exact packaged modules. Future collections use used_by.
