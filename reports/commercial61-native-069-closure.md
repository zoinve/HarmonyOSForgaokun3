# Native 069 Closure

Run: commercial61-native-069-c29bce77-f24f-4624-9b59-98c579aeae41.
Original diagnostic timeout completed and Ubuntu returned. Desktop goal remains
active and unverified. This experiment must not be rerun.

## Preservation

post-return-verification.json confirms Ubuntu current/default, unchanged
firmware and four original images, 131 unchanged prior EFI files, retained
manual entry, unmounted lab partition and enabled/active screen-off timer.
Only boot-managed random seed and authorized archived entry 067 removal differ.

## Rendering

All 67 retrieved files verified. Render and presentation analyses completed:
first flush 77.94 guest seconds, last frame 150.033238, 71 post-flush frames.
Full trace EOF verified. Full-resolution capture is byte-identical to 068:
4652 nonblack pixels among 4096000, zero differences between clockwise-rotated
source and completed scanout. This proves one frame copy, not desktop success.

## Resource Inventory

StartupGuide PID 5539 was sampled ten times. Original preinstall HAP exists;
its parent contains only HwStartupGuide.hap. The application bundle bind exists.
Sandbox bundle root contains shared dependency directories, but module
pc_hwstartupguide, extracted resources.index and checked videos are absent.
The original HAP contains the welcome videos with valid ZIP CRCs.

Observer realpath fields are NOT application-namespace realpath evidence:
canonicalization of /proc/PID/root may continue in the observer namespace.
Use proc-root stat/open results and original application errors instead.
An app-invisible host public path does not establish host-side absence.

## Next Decision

Determine actual resource-manager input path before any layout repair.
Offline original ELF inspection confirms HapResourceV1 constructor at 0x5b434
copies its path and passes it to HapResource at 0x5b484. Base constructor
0x640d0 copies that string unchanged into object offset 0x98 at
0x6410c..0x64114. This proves storage, not the actual runtime argument.

No private runtime objects were read or patched. No resource interposition,
provisioning bypass, installed-record fabrication or force-stop was adopted.
See reference-oobe-resource-followup-067.md for all three reference roles.
