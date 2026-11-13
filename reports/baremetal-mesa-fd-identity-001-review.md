# Mesa FD-identity regression and isolated rebuild

## Root cause established

`baremetal-mesa-fd-identity-audit-001.json` records the actual Mesa002 compile command, preprocessor macros and ARM64 object disassembly. With `auto_features=disabled`, `allow-kcmp=auto` did not enable `ALLOW_KCMP`. `os_same_file_description` compared the integer descriptors and otherwise returned -1 without setting errno or invoking kcmp. Therefore the GPU warning's ENOENT was stale errno, not evidence that a kernel comparison returned ENOENT.

## Actual OHOS CPU-only tests

- Probe001 called the raw kcmp syscall as uid1001 with no-new-privileges. A duplicate descriptor compared equal (0); independently opened descriptors compared different (1); both had errno0. A separate F_DUPFD_QUERY diagnostic also distinguished them. This was on the running Ubuntu kernel, not a new native-kernel GPU run.
- Probe002 compiled the old Mesa object regression but its exclusive remote-stage guard refused an inadvertently reused path before executing the probe. Its compile/transfer/failure records remain unchanged.
- Probe003 corrected only fresh deployment paths and linked Mesa002's actual `os_file.c.o`. Under the same unprivileged OHOS runtime it returned **-1/errno0 for both duplicate and independent descriptors**, exiting 1 as the regression requires. The raw optional query still distinguished the descriptors. `reports/baremetal-fd-identity-probe-003/result.json` retains the failed functional result; it is not relabelled as a passing comparison.

These CPU probes access genuine `/dev/null`, not a GPU. Their programs verify uid1001 and no-new-privileges; the transient unit properties are requested controls, not a separate live effective-policy capture. No security permissions, identities, SDK images or Ubuntu libraries were changed. Boot ID stayed `6c8229ac-31cf-4ac6-9de7-3794b3f7d1eb`.

## Controlled next step

Mesa003 builds into new work/staging/report directories with the same Mesa source and driver options, plus explicit `allow-kcmp=enabled` and a distinct install namespace. It hashes the entire previous Mesa002 work tree and protects the existing source and legacy prefix. There is no source patch, system installation or device access in the build.

Mesa003 completed successfully. Independent verification checked all 34 staged artifact hashes and sizes, the explicit enabled option, and the actual ARM64 comparator object containing getpid/syscall calls. The original sources, legacy prefix and entire previous Mesa002 work tree were preserved. Probe004 linked the new actual object and passed as uid1001/NNP: duplicate descriptors returned 0/errno0, independent descriptors returned positive 2/errno0. Positive values mean different descriptions; they need not equal 1.

## Same-executable hardware regression

`baremetal-freedreno-fence-package-002` reuses the exact previously proven fence executable (SHA-256 `3f124cf9743ab84e0b8732853743cbe6130235e3dcbdd17e1810fb4bf069468e`) rather than recompiling it. Only five Mesa shared libraries changed; the OHOS SDK loader, libdrm and libc++ remained unchanged. The new archive contains nine verified AArch64 ELF files with resolved strong dynamic symbols, 6,404,000 bytes, SHA-256 `7730e43e32fc2d87d436d22808a65100331210b9a8d77ea44da70ed8cb66d1a4`.

`baremetal-freedreno-fence-run-002/result.json` records the actual hardware pass on the running Ubuntu kernel: FD690, exact opaque red/blue GLES pixels and second-device DMA-BUF CPU-map pixels, native fence poll and EGL reimport/signalled status. Exit status was 0, no additional kernel log was captured, and the FD-identity warning was absent. Pre-execution effective policy was captured for both sandbox admission and GPU units: unprivileged user/render group, renderD128 only, empty capability bounding set, NNP and private network, strict filesystem protection and resource bounds. The independent post-run asset/screen/default audit is recorded separately when complete.

The initial independent verifier stopped locally because it expected versioned build filenames instead of the bundle's documented SONAME filenames. Correcting those five expected paths does not change the package, GPU run or its result. No GPU rerun was needed.

This new-library regression is **on the Ubuntu kernel**, not an additional own-native-kernel run or a HarmonyOS desktop. Native trial007 still accurately records the old library build's hardware success and its warning. A fresh native diagnostic is needed to validate Mesa003 under the reduced native sandbox before superseding that runtime result.
