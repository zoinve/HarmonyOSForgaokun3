# Candidate 011: single-factor Mesa file-description comparison regression

011 changes exactly five Mesa libraries relative to the native-GPU-passing 010 archive. The native profile003 kernel, DTB, all matching modules, diagnostic init source/binary, identity helper, namespace launcher, GPU test executable, original SDK loader, libdrm and C++ runtime remain unchanged. No new security permissions, identity writes, modesetting or policy loading are introduced.

The Mesa change is explicit `-Dallow-kcmp=enabled`. The previous global `auto_features=disabled` prevented the actual Mesa function from calling `kcmp`; it returned -1 without setting errno. The original function failed a real rootless duplicate-versus-independent FD regression. The new function passed it. The unchanged fence executable also passed GPU rendering, DMA-BUF second-device readback and native-fence tests with the five new libraries under Ubuntu; the old warning was absent. This is not yet a repeat under the diagnostic kernel and its UID65534/PID namespace sandbox.

## Actual archive verification

- Archive: 31,256,183 bytes; SHA-256 `9737f1ad608b34e91750be64fc7360be4ac407ab1fd0ffb4a44eb721973efb84`.
- Native kernel SHA-256: `4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`.
- Initial package construction and a separate archive parser both proved that only these records changed:
  - `opt/native-mesa-001/lib/libEGL.so.1`
  - `opt/native-mesa-001/lib/libGLESv2.so.2`
  - `opt/native-mesa-001/lib/libgbm.so.1`
  - `opt/native-mesa-001/lib/libgallium-25.0.1.so`
  - `opt/native-mesa-001/lib/gbm/dri_gbm.so`
- All other 010 archive records have identical content, modes, UID and GID. All 620 inert-parent records remain preserved. The launcher was copied byte-for-byte, not rebuilt.
- Evidence: `baremetal-diagnostic-init-011/result.json` and `baremetal-diagnostic-init-011/independent-verification.json`.

## Remaining validation

The six assets were staged in the independent `native-identity-diagnostic-011` lab directory, with every size/hash verified and all three executable ARM64 refusal checks returning 77. All 226 saved trial007 raw files were verified locally and remotely before and after restoring only lab preparation mount flags.

Fresh preflight008 confirmed the 13 original loader configurations, post-cleanup baseline, no pending one-shot and active Ubuntu screen-off timer. Installer008 installed only the independent 011 entry/assets; all 79 pre-existing EFI files were unchanged at installation and Ubuntu/firmware defaults were retained. Reconnect and screen-off policy suites each passed four checks again. Trial008 subsequently returned to Ubuntu: the unchanged fence executable passed native GPU pixels, second-device DMA-BUF mapping and native fence checks with the FD warning absent. All 264 raw files and already-off Ubuntu state were independently verified. Cleanup005 archived and removed only consumed011, preserving the other 82 EFI files and all assets/logs. See `baremetal-native-trial-008-review.md` for actual results and limits.

Native execution must independently demonstrate the same shader pixels, second-device DMA-BUF mapping and native fence results, absence of the FD warning, successful cleanup and Ubuntu return. Existing 25-second GPU phase admission, 180-second best-effort deadline and 30-second reserve remain unchanged; these cannot guarantee recovery from a kernel hard lock.

Initial SELinux enforcing without a loaded policy is not loaded-policy authorization evidence. Offscreen GPU success is not HarmonyOS desktop, physical scanout or touch interaction evidence. Ubuntu remains the persistent default, with automatic logical screen-off and immediate SSH observation after any authorized diagnostic reboot.
