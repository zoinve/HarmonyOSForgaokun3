# Native diagnostic 004: offline readiness boundary

This is a Linux hardware diagnostic candidate, **not a HarmonyOS boot image**.
Authorization remains offline preparation only. No EFI installation, default-entry
change, native boot, reboot, or authentication modification is part of this work.

## Artifact set (on the isolated lab partition)

- Kernel: `/mnt/harmony-lab/work/native-build-001/artifacts/arch/arm64/boot/Image`
  - SHA-256: `f304d26414e27122716d8b6199c0d096bb314d80dc5f32fa3300dd97420523d0`
- DTB: `/mnt/harmony-lab/work/native-build-001/artifacts/arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb`
  - SHA-256: `2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32`
- Initramfs: `/mnt/harmony-lab/work/native-diagnostic-init-004/diagnostic-init.cpio.gz`
  - SHA-256: `884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1`
- Candidate release: `7.1.0-rc3-gaokun3-el2`, **without** the running Ubuntu
  kernel's trailing `+`. Do not substitute Ubuntu's modules or initramfs.

## Verified offline

| Check | Evidence | Limit |
| --- | --- | --- |
| 391 packaged modules match candidate build; 12 firmware files match staged copies | `baremetal-diagnostic-004-artifact-coherence.json` | Not a complete hardware/firmware closure proof |
| ARM64 Image/EFI application format; correct board DTB; five DTB firmware paths present | `baremetal-diagnostic-004-image-dtb-audit.json` | Firmware loading and physical execution untested |
| 15 observed device modaliases resolve to expected candidate modules | `baremetal-diagnostic-004-device-alias-audit.json` | Historical Ubuntu observations, not candidate probe success |
| gzip initramfs, ELF, devtmpfs, proc, sysfs, ext4 and module support enabled | `baremetal-diagnostic-004-kernel-requirements.json` | Configuration is not execution evidence |
| 21 targeted userspace/source-contract tests | `baremetal-diagnostic-004-tests.txt` | No actual PID1, mount, module, or reboot test |
| Four archives preserved; loader files and firmware boot entries unchanged | `baremetal-diagnostic-004-independent-verification.json` | State at that audit, not a future boot rollback guarantee |

## Gates still open

1. **Recovery:** no verified independent recovery medium or hard-lock recovery.
   The stale WINPE firmware entry is not such evidence. Pstore is unavailable.
   The 180-second userspace reboot helper cannot recover a kernel hard lock.
2. **Hardware execution:** actual PID1 startup, storage discovery, DRM/panel/input
   probing, persistent logs, unmount and return to Ubuntu have not been exercised.
   The 30-second finalization reserve is admission policy, not an I/O deadline.
3. **HarmonyOS ABI:** native kernel has no verified SDK 7 identity/Binder extension
   integration. Basic token calls do not cover parent-token and SPM operations.
   See `baremetal-sdk7-identity-abi-gap-001.md`; do not replace missing operations
   with success, fabricated tokens, permission grants or authentication edits.
4. **Native graphics integration:** VM VirGL output is not proof of native Adreno
   rendering or HarmonyOS composition on MSM/DSI. The observed physical panel mode
   is 1600×2560 portrait, not the earlier VM's 3120×2080 setting.

No boot entry is supplied or installed by this report. A future hardware test
requires separate boot authorization and an explicit recovery arrangement; neither
is inferred from permission to continue offline preparation.
