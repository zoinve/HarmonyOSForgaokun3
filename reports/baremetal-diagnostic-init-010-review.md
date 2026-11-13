# Diagnostic 010: native-kernel/OHOS Mesa offscreen joint test

The 31,255,670-byte archive has SHA-256 `f00ae673e495abbd521628418badbc16d7f12d72d40236855b0a7f149e0e5afb`. Independent parsing verified all 620 parent records (contents, modes, owners) unchanged and exactly 17 additions, including nine unchanged original fence-probe runtime ELF files and the known relative libc symlink. Native profile003 kernel/DTB and helper002 hashes match their prior verification.

The only diagnostic-flow addition after enumeration is a 25-second offscreen Mesa phase. The existing 180-second best-effort deadline, 30-second admission reserve, identity reads and working display/touch module requests are retained. These are not hard-lock recovery guarantees.

The static launcher creates private mount/network/PID namespaces and a read-only bundle, then permanently drops to UID/GID 65534, no supplementary groups, zero capabilities and no-new-privileges. Its device view excludes primary DRM, input and storage nodes. It exposes only the render node and genuine kernel basic character devices; the original OHOS loader executes the unchanged previously tested fence probe. Resource limits and the outer diagnostic timeout apply. No window, modeset, token setter or policy load is added.

Host checks exercised admission, actual CPU-only namespace isolation, renderer/pixel rejection, DMA-BUF metadata and four actual C snapshot cases; these are not GPU evidence. ARM64 QEMU048 initially stopped earlier than intended because the test initramfs omitted the bundle bind directory. The failure is preserved. Fresh QEMU049 supplied only that empty fixture directory: the unchanged launcher then refused the missing render node with status126, removed its mountpoint, and separately refused missing diagnostic opt-in with status77. No GPU or disks were attached.

010 subsequently booted on the board in trial007: the native-kernel/OHOS Mesa offscreen shader, native fence and second-device DMA-BUF readback completed with status0. Ubuntu returned and all 226 collected raw hashes were independently verified. See `baremetal-native-trial-007-review.md` and its machine-readable evidence. Initial SELinux enforcing state without a loaded policy must not be described as policy-authorized GPU execution or a HarmonyOS desktop.

HarmonyMac remains the confirmed reference project. The second user-provided reference has not been identified in the restored record; no claim is made that both have been reviewed.
