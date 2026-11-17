# Native Input and USB 148 Closure

## Scope and Preservation

User priority: touchscreen and USB on the user-confirmed desktop baseline.
One bounded native boot completed; no OOBE or activation work was performed.
The only initrd differences from 145 are `init` and its verified early wrapper.
Original kernel, modules, DTB, desktop runtime, seed and service binaries remain
unchanged. USB mode was not changed. Audio work remains paused.

The bootstrap now loads the exact packaged `usb_storage`, `uas` and `exfat`
modules, with a 12-second group admission and 4 seconds per probe, no retry on
timeout. This adds a real storage backend without mounting or writing USB media.
Read-only metadata sampling runs at least 20 seconds apart and consumes no
input events. It exports supported axis limits, not current touch values.

## Actual Native Results

Evidence directory: `commercial61-native-148/runtime-evidence`.
Run: `commercial61-native-087-e928c4f9-8c26-437f-bd19-3eeb4e886762`.
Latest phase: `phase-172.log`. All 188 retrieved files match their hashes.

- All three storage module probes returned zero. All three modules subsequently
  report `initstate=live` in native runtime sysfs.
- Five metadata samples were captured, all complete. Original MMI is observed
  holding real evdev descriptors across the later runtime samples.
- Himax touchscreen: X and MT X 0..2559; Y and MT Y 0..1599; ten slots 0..9.
  This matches the intended 2560x1600 logical desktop, unlike Ubuntu's own DTB.
  Physical corner accuracy and drag/multitouch remain unverified.
- Original MMI holds the Himax node and the USB detachable keyboard/touchpad
  nodes. Node numbers are observations only, never a device-selection contract.
- Original USB host, USB service, extended HDF manager, storage daemon and
  storage manager processes appear in runtime samples. Process presence does
  not establish successful device enumeration or file operations.
- Outer initramfs USB device nodes exist. Their outer mode is 0600 root:root.
  **This is not proof of a service permission fault**: the original-service
  bootstrap replaces `/dev` with a separate tmpfs. Service-visible metadata
  must be sampled via `/proc/<pid>/root/dev`, not inferred from outer nodes.
- No USB-device fd was captured in the sampled services. This does not prove
  an open attempt failed, nor that a descriptor is never opened transiently.
- The inherited runtime has a synthetic LEFTMETA diagnostic. It is not physical
  keyboard input and cannot be used as physical HID acceptance.

Structured analysis: `commercial61-native-148/input-usb-runtime-analysis-148.json`.

## Original Contract Audit

`input-usb-contracts-149/result.json` records original MMI/USB/storage services
and uevent rules. It is configuration evidence, not current permissions.

`usb-implementation-151/result.json` resolves all three real USB implementation
ELFs, including fast symlinks missed by the initial 150 collector. 150 evidence
is retained unchanged; its unresolved adapter/shared rows do not prove absence.

The original host HDI depends on the genuine adapter and libusb backend. The
backend includes Linux usbfs and `/dev/bus/usb` support and expects read/write
device access. The missing HDI release-symbol warning alone is not sufficient
reason to replace or patch the original host implementation.

## Verification and Return

- Full ordered 28-archive chain equals the full candidate initrd.
- Packaged storage-module hashes, unchanged runtime/seed payloads and isolation
  guards passed. Eleven focused test scripts passed in admission, plus parser
  tests and fast-symlink resolver tests passed separately.
- Phase evidence records the bounded target timeout, target exit and native
  diagnostic end. Ubuntu return is independently observed.
- Returned Ubuntu boot ID: `94e4f95e-cd09-4703-bda2-6dbd2029dadc`.
- Ubuntu remains current/default; one-shot consumed; timer enabled and active.
- 173 prior EFI files unchanged; only normal random-seed change and the
  archived, user-authorized removal of the 141 entry are accounted for.
- Firmware and four original image hashes match; LAB partition is unmounted.
- Retained experimental entries: 145 and 148. Original manual entry preserved.

## Next Required Work

Sample actual service-root input/USB node permissions and major/minor identities,
and compare them to genuine kernel sysfs records before making any node fix.
Do not chmod outer nodes, expose NVMe block devices, or enable a storage path
that can write unknown media. Physical taps/drags, external USB HID hotplug and
USB storage file access remain acceptance gaps. Overall driver goal is active.
