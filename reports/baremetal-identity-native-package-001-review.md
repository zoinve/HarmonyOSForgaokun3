# Identity-patched native package 001 — inert preparation

This packages the independently verified identity candidate's native kernel and **all 391 modules from that build**, not modules from the running Ubuntu kernel. No device-side file was written, no entry was installed and no reboot was requested.

- Kernel SHA-256: `8ba8c0049c3608e3a72769897e718051c78addb4d73a29699714f2e49f576457`.
- Board DTB SHA-256: `2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32`.
- Module inputs were individually size/hash checked against the independent candidate inventory.
- Fresh `depmod` completed without warnings; all 391 dependency records point to present files.
- All 43 non-module entries retained their original bytes and modes, including the existing limited firmware set, userspace tools and dynamic dependencies.
- The original remote base was copied read-only and hash-verified; it was not modified.

The resulting inert archive is byte-identical to base 002 (`ff0a661c831f950ebad0cd69c91b21d999bffce6f2bc49601e2cb7253ab5219c`, 23,909,120 bytes). This is a measured result: all selected rebuilt module bytes and regenerated metadata match those previously packaged. It does not mean the new kernel is unchanged, nor establish runtime compatibility by itself. The new kernel must still be paired with a verified diagnostic init and tested on the board.

`baremetal-identity-native-package-001/result.json` records the complete module inventory and preservation checks. The archive contains no `/init` and is not a boot-ready experiment. It does not contain a HarmonyOS system or prove full firmware coverage, physical display/touch operation or HarmonyOS desktop readiness.
