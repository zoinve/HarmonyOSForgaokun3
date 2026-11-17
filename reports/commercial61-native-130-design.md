# Native Panel Backlight 130

This is a basic-driver integration experiment, not an OOBE/activation experiment. Keep the user-accepted desktop seed, original runtime 108, original services and GPU composition unchanged.

## Evidence And Change

Run 124 original RenderService requested display 0 backlight level 11363; composer_host and RenderService reported failure. The project's composer 075 implements both backlight entrypoints as unconditional UNSUPPORTED. The L410 reference uses a native HDI maximum of 65535, unlike the 0-255 DisplayManager UI interface. The real gaokun3 panel's maximum is read from sysfs (currently 4095).

Composer 129 replaces only GetDisplayBacklight/SetDisplayBacklight with the real sysfs backend and 65535-range conversion. At the observed request 11363 this yields hardware brightness 710. Invalid display IDs, levels, pointers, missing attributes, malformed data and write errors are propagated. No cached/fabricated brightness is returned. Existing public exports and the original commercial runtime-library dependency closure are preserved; no SDK runtime DSO is linked.

130 changes exactly three initrd members: init, its integrity wrapper and the project's composer DSO. The original namespace runtime and all other member modes/content are byte-identical to 123/124. A narrow pre-service rule verifies sysfs magic on the real backlight directory, opens only the existing brightness attribute without following a leaf symlink, and assigns root:3036 mode 0660 for the original composer group. It does not change service credentials, policy, Ubuntu or unrelated attributes. Kernel reboot resets this guest-only sysfs inode state.

## Gates

- Seven backend tests, two composer-glue tests and three existing seed tests pass. Strict AArch64 builds and three PID1 isolation guards pass.
- Independently merging all 27 entry archives exactly equals the full 130 initrd. The same command-line length guard remains below 1800 bytes.
- Installation verifies source/runtime/seed hashes, existing kernel/DTB/overlays, EFI free-space margin, Ubuntu default and enabled/active screen-off timer. Existing EFI files and firmware remain unchanged during installation.
- Retain only experimental entries 124/130. Archive removed 123 entry content/hashes outside ESP first; do not remove shared payloads or the original manual entry.
- Boot once with the existing bounded return. Retrieve read-only/noload with physical-serial, UDID and credential checks. Then verify all original image hashes, firmware, default boot and timer.

## Acceptance

Look for the narrow permission marker and the real composer SET/GET result when called by original services. Correlate the original RenderService request with composer return and original error logs. Preserve full-resolution display and input evidence. A successful backend write establishes sysfs access, not human-perceived slider correctness, physical luminance, sleep/wake or complete power management. Those remain separate acceptance checks. Battery, audio and Bluetooth are not changed by this candidate.
