# Basic Driver Integration 002

Date: 2026-11-16. Goal remains native basic-driver integration using the
user-confirmed desktop baseline. No further activation/OOBE changes.

## Verified Progress

- Backend: seven focused sysfs tests cover optional real battery readings and
  the native backlight range of 0-65535, not only the UI range of 0-255.
- Composer 129: original Get/SetDisplayBacklight unsupported stubs replaced
  with real panel access; public exports and unrelated graphics code retained.
- Operational 130: original RenderService backlight request completed without
  its prior unsupported error. Hardware write/readback is still unverified:
  composer stderr markers were absent from retrieved evidence. See
  commercial61-native-130-closure.md for exact acceptance limits.
- Keyboard delivery to original SceneBoard confirmed again; visible input
  interaction, touch alignment and gestures remain unverified.
- Original images, firmware, Ubuntu default/manual entry and active screen-off
  timer passed post-return preservation checks. Retained entries: 124/130.

## Battery Candidate 131

The real battery auxiliary device was unbound in run 130. The packaged module
lib/modules/7.1.0-rc3-gaokun3-el2/kernel/drivers/power/supply/huawei-gaokun-battery.ko
has SHA256 7d108cc20c45bf6d112014576073f81191758beaf75d9cd726daeedec18dc322.
The explicit module list omitted it. Candidate 131 loads it immediately after
the EC and adds a bounded read-only supply/binding probe. It does not create
sysfs aliases, synthetic supply values or modify a battery service binary.

The first offline build failed on generated C quoting; its source and stderr
are preserved in commercial61-native-131-build-failed-001 in the build root
and reports. The corrected build passed -Wall -Wextra -Werror for ARM64.
Only init and early-hardware093.sh archive members differ from 130. Overlay
SHA256: dfed299c0bb82b8c4395b94dccece19aba5c5e9bfc2541c279d876706ca2efaf.
Candidate 131 is NOT installed or booted; it has no runtime/HDI/UI acceptance.

## Remaining Acceptance

1. Admit and boot 131 once; verify real EC battery binding/readings and charging
   state. Then connect real supply discovery to the original Battery HDI 2.0
   contract without its mock fallback or fabricated optional readings.
2. Add durable backlight result/readback evidence; validate UI brightness.
3. Verify touch/touchpad coordinates, scrolling and USB hotplug through MMI.
4. Validate native network supplier/IP/DNS, then Bluetooth transport/pairing.
5. Integrate board-specific ALSA routing and original audio interfaces. This
   board uses WSA883x/WCD938x, not the L410 TAS amplifier sequence.
6. Exercise suspend/resume only after basic service and hardware acceptance.
