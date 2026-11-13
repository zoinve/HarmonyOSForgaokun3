# Original-SDK device and security profile 003

## Why this profile is needed

The unchanged production SELinux policy loaded in isolated QEMU test 019, stayed enforcing, allowed its original init domain to use a correctly labelled RAM console, and denied that domain access to a wrongly labelled console. This is not a service boot.

Test 020 did not reach its identity assertions: its attempt to discover the traditional Binder misc device failed with `ENOENT`. The candidate's actual `drivers/android/binder.c:binder_init()` registers those misc devices only when `CONFIG_ANDROID_BINDERFS` is disabled. Its current BinderFS setting therefore differs from the original SDK's `/dev/binder` device expectations. No token/Binder authorization success is inferred from this failure.

The original binary policy's static AV audit also distinguishes roles: init may open the original token/Binder device labels, but may not become Binder context manager; samgr may become context manager. Earlier isolated IPC tests did not have active SELinux and cannot establish that the same tests pass under production policy.

## Bounded change and verified build

`next-experiment/build-baremetal-identity-profile-003.py` creates a fresh source copy and output directories. It requires exactly two native configuration changes relative to identity candidate 002:

- Disable BinderFS, enabling the existing traditional `binder,hwbinder,vndbinder` misc-device configuration.
- Add `selinux` before `bpf` in the existing LSM list, retaining every previously selected LSM.

Binder/token source bytes, permission rules, 4 KiB pages, seccomp and watchdog configuration are not changed. `enforcing=1` remains a required boot argument: this profile deliberately retains the existing SELinux development configuration rather than falsely claiming enforcing is its default.

The separate QEMU output may change only PL011 console selections. No resulting kernel has been installed, selected or booted on MateBook. Existing SDK images, Ubuntu, boot defaults, old candidates and old evidence remain outside this build's write scope.

The build completed in about 658 seconds. Independent verification checked all six native/test artifacts, all 391 modules, both configuration hashes, and equality of the local and WSL result records. Native Image SHA-256: `4e7796bda71bdc95364276bbff34eb2c72593a2a9a3baa7fe2b9e5ae86e65166`; test Image: `b5f16aa3c807734c69780ff7014fc56151906067f24960cb896755b5e996dcf5`. See `baremetal-identity-profile-003/independent-verification.json`.

## Runtime verification and fixture corrections

Test 021 reached the real legacy devices but correctly encountered production-policy denial of init reading their SELinux metadata. The separate binary-policy AV audit confirms `getattr` is denied while open/read/write/ioctl are allowed; successful label assignment does not imply permission to query it afterward. Test 022 checks those metadata denials but then encountered another correct policy denial: init may not issue SPM version ioctl `0x4119`.

Original CIL rules permit init's SPM request `0x4110` but reserve version `0x4119` for `accesstoken_service`. Test 023 therefore separately verifies version-query `EACCES` and allowed-but-unimplemented request `EOPNOTSUPP`, with both output buffers unchanged. Its serial log contains all positive/negative PASS markers, including Binder protocol 8/features 5 and context-manager refusal. Its runner nevertheless failed because an old exact-string matcher expected the previous marker fields; this failed result is preserved. Test 024 repeats the exact 023 binary, kernel and original policy with only that matcher corrected. Its result must be checked separately before asserting runner success.

No policy, kernel, device permission, identity authorization or enforcement rule was relaxed to accommodate these fixture expectations. Device-label evidence consists of successful original-label assignment plus the actual labelled AVC records, not successful metadata reads from an unauthorized domain.

Neither a successful build nor these checks alone establish a faithful SDK service boot, original SDK IPC under enforcing, native display operation under that policy, or a HarmonyOS desktop.

### Test 024 result

The corrected runner passed in about 1.23 seconds using the exact prepared 023 init and unchanged profile-003 test kernel and production policy. It verified real legacy devices, token roundtrip/restoration, non-owner denials, metadata denial, policy-blocked SPM version query, allowed-but-unimplemented SPM request, Binder protocol 8/features 5 and init's context-manager refusal. The latter refusal is observed at the ioctl permission filter (`0x6207`), so this test does **not** independently prove execution of the later Binder context-manager security hook.

Independent verification checked both prepared artifacts, the actual test-kernel hash, equality of WSL/local result JSON and serial bytes, and all positive/negative markers without a probe failure or kernel panic. Serial SHA-256: `22d33f8814dd9847dd4fe3237c77d365d805fcb8ee97885c203d988afe722191`; see `baremetal-selinux-qemu-024/independent-verification.json`. Expected AVCs remain in the raw log; they are not suppressed.

This is isolated QEMU kernel ABI evidence under enforcing policy, not original SDK service execution or a physical-board test. No MateBook reboot or installed configuration change occurred during this profile's work.
