# Input and USB priority, 2026-11-16

The user's current priority is touchscreen and USB. Audio work is paused at
the 145 real ALSA registration milestone. The working desktop/runtime/seed,
rotated HarmonyOS DTB and Ubuntu default remain unchanged in this step.

## Native baseline 145

Source: `commercial61-native-145/runtime-evidence/raw/interactive-hilog030.log`.

- Line 22820: original MMI successfully registers the SPI touchscreen device.
- Lines 22773 and 22798: original MMI successfully registers the USB detachable
  touchpad and keyboard. The USB device identity is 12d1:10b8.
- Line 22815: touchscreen open returns a valid fd (31). The logged errno 22
  does not by itself mean open failed; it appears beside successful opens for
  multiple devices and is followed by successful registration.
- Line 11478: host HDI loader warns about an absent release symbol; later host
  implementation logs exist. This warning alone does not prove host failure.
- Lines 11248-11251: USB accessory/device interface lookup fails. This is not
  sufficient evidence that host HID is broken: host HID registration above
  succeeds independently.
- No physical corner accuracy, drag, multitouch, external USB mouse or storage
  acceptance has been established by these observations.

Do not hardcode the observed native event numbers into any implementation.
Do not infer current commercial cursor behavior from old SDK adapter results.

## Read-only Ubuntu metadata

Accepted metadata collection:
`input-usb-147-20261116T035108689143Z/result.json`.

- Himax axes: ABS_X/ABS_MT_POSITION_X 0..1599 and
  ABS_Y/ABS_MT_POSITION_Y 0..2559; ten touch slots (0..9).
- Ubuntu currently assigns the touchscreen event11. This is not the native
  HarmonyOS event number or coordinate configuration: Ubuntu boots its own DTB.
  Do not replace the existing HarmonyOS transform based on these raw ranges.
- USB detachable 12d1:10b8 has two bound usbhid interfaces. Its vendor-specific
  interface has no driver; that is not a reason to replace working HID drivers.
- Three xHCI root-controller pairs enumerate. Both Type-C ports report host
  data role; one supplies power and the other consumes power.
- No USB storage block devices were attached at collection time. No assertion
  about storage failure or successful file access follows from this empty list.
- Ubuntu has uas and usb_storage loaded. The native 145 initrd contains
  usb-storage.ko, uas.ko and exfat.ko; init.c has no explicit storage-module
  loading. Native module state and service behavior need direct observation
  before selecting a storage bootstrap change.

Collector `collect-input-usb-147.py` reads sysfs metadata, permissions,
EVIOCGBIT(EV_ABS) and EVIOCGABS. It never reads evdev events, exports the current
axis value, changes USB role, mounts target partitions or changes drivers.
The focused tests pass (3 tests), including filtering unsupported axes and
checking the AArch64/Linux ioctl request layout.

Earlier collection `input-usb-147-20261116T035024244023Z/result.json` is retained
unchanged but superseded: it queried unsupported ABS axes without first checking
the capability mask. Some unsupported axes consequently appear as zero ranges.
Use the accepted later collection above, not those zero-valued extra axes.

## Next Native Verification

1. Add bounded metadata sampling for evdev capabilities/axis ranges, actual
   original MMI input fds, USB device-node permissions and bound USB interfaces.
   Keep current coordinate transform and host mode unchanged.
2. Compare native storage-module state with the packaged modules. Add bounded
   loading only where the native evidence establishes a missing backend.
3. Verify finger taps at four corners and center, drag and multitouch in the
   actual desktop. Synthetic injection is not physical-touch acceptance.
4. Verify external USB keyboard/mouse insertion and removal, then attached
   storage enumeration and original storage-service integration. Do not write
   to unknown USB media during initial diagnostics.

This step performed no reboot or original-image write. Experimental entries
141/145 remain the current retained candidates. Overall driver goal is active.
