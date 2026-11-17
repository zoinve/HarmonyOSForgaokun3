# Native Service Device Namespace 152

One bounded native boot completed and returned to Ubuntu. Source images,
runtime, seed, kernel, modules and DTB remain unchanged. No permissions were
modified and no input events or USB media contents were read by the sampler.

Run: `commercial61-native-087-afff1c2d-e4df-4281-8425-09d50e2f21e8`.
Evidence: `commercial61-native-152/runtime-evidence`, 185 files, all hashes match.
Structured result: `commercial61-native-152/service-devices-runtime-analysis-152.json`.

Four complete samples resolve the actual service-root `/dev` through procfs,
verify private tmpfs and compare character-device identities with kernel sysfs.
The last sample contains six services, 108 nodes, zero missing nodes, zero
refused service roots and zero major/minor mismatches. Each service sees eleven
input nodes and seven USB nodes.

- Input nodes are root:input (gid6696), mode0660. Original MMI holds the Himax
  touchscreen and detachable USB HID descriptors.
- USB nodes are usb_host:usb_host (uid/gid3023), mode0660, with real major189
  and matching kernel minor numbers. The USB/hdf service groups include3023.
- The kernel-visible detachable device is `/dev/bus/usb/005/002` in this run.
  Addresses and evdev numbers are observations, not implementation constants.
- The vendor text rule root:ueventd does not describe the observed effective
  permissions. The original system rule already applies successfully here.
  Do not patch rules or chmod nodes based on the offline rule discrepancy.
- The outer initramfs's root:root0600 modes are unrelated to the service view.

This rules out missing service-root input/USB nodes and incorrect observed
node ownership as the current gap. It does not establish public USB-service
enumeration, physical touchscreen accuracy, external HID hotplug or storage
file access. Next verify the original native USB backend and public service
without changing device configuration or security checks.

Full ordered initrd chain, exact payload delta and twelve admission test scripts
passed. Three separate parser tests passed. Ubuntu returned with boot ID
`832de3d6-47a8-4762-a07a-9d538f51011e`; default/current entry and enabled/active
screen-off timer match requirements. Firmware and all four source-image hashes
match, LAB is unmounted. 174 prior EFI files unchanged, normal random-seed
update and archived authorized removal of the145 entry accounted for. Latest
two experiment entries are148/152; original manual entry remains.

No permission repair is justified by this evidence. Overall driver goal remains
active; touchscreen/USB remains the user's priority and audio is paused.
