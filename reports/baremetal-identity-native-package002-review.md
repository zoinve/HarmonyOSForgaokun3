# Native identity profile-003 package 002

The offline package contains the actual native profile-003 kernel, its matching DTB, and 391 hash-checked modules. It does not contain the QEMU-only VirtIO storage configuration. It has no `/init` and is therefore not an installable or boot-ready diagnostic by itself.

- Kernel: `4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`.
- DTB: `2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32`.
- Native configuration: `5287121e1fafde20e2562a7fb74f1bcac0273cb180401506cb1e2fd91af669d7`.
- Inert archive: 23,909,120 bytes, SHA-256 `ff0a661c831f950ebad0cd69c91b21d999bffce6f2bc49601e2cb7253ab5219c`.

The archive being byte-identical to the previous base is a measured result: the selected module bytes and regenerated dependency metadata are unchanged. This does not mean the kernel is unchanged. Legacy Binder devices and the active SELinux LSM selection are built into this new kernel. Explicit `enforcing=1` remains required. All 43 nonmodule base entries were preserved by byte content and mode; depmod produced no warnings and every dependency path exists.

Independent package verification passed: archive byte count and SHA-256, all 391 packaged modules against native build records, native kernel/DTB/configuration, and absence of QEMU-only VirtIO profile changes. See `baremetal-identity-native-package-002/independent-verification.json`.

No package was installed on the MateBook, no boot entry was added, and no physical reboot occurred. Profile-003 full original-SDK service boot remains a QEMU result; native-board evidence so far is the earlier profile-002 read-only identity/display/touch diagnostic, not this new profile's enforcing userspace.
