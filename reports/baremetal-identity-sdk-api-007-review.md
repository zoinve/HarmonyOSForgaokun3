# Original SDK token API regression 007

The original OHOS loader and unmodified `libtokensetproc_shared.z.so` / `libsec_shared.z.so` ran against the patched real kernel in diskless QEMU. Preparation verified the token library byte-for-byte against a fresh read-only extraction from the original system image.

The run retained the raw ioctl, synchronous/one-way and nested Binder checks (`IDENTITY007_PASS checks=185`) and additionally reported:

```
SDK007_SPM version_result=95 version=0
SDK007_PASS checks=13 original_library=1 spm_unsupported_honestly=1 services_not_tested=1
```

The 13 parent-process API assertions include successful subprocess results; additional assertions execute inside those subprocesses and are not included in that counter. They cover original-library self/first-caller read/write, exec/fork inheritance, unprivileged mutation denials, authorized supplementary-group access and parent/child identity isolation. Unsupported SPM version returns positive `EOPNOTSUPP` (95) with version zero. Unsupported parent-token lookup returns that error without changing the supplied output. No unsupported command is reported as successful.

## Test-environment correction

The preserved 006 run failed when an unprivileged original API call reopened the node and encountered `EACCES`. Earlier raw ioctl checks intentionally used inherited descriptors. Read-only extraction confirmed the SDK's `/system/etc/ueventd.config` contains exactly:

```
/dev/access_token_id 0666 3020 3020
```

Fresh 007 applies that device-node ownership and mode only inside the opted-in diskless QEMU guest before the SDK test. The supplementary-group API test correspondingly uses group 3020. This reproduces the original SDK's filesystem policy; it does not change driver authorization checks, physical-machine permissions or SDK images. The kernel was not rebuilt between 006 and 007.

## Independent evidence and limits

`baremetal-identity-qemu-007/independent-verification.json` verifies all four packaged SDK files and local/WSL serial-log equality. The kernel, native configuration and critical source preservation checks are recorded in the run result.

This verifies the listed original token APIs, not all SPM callers' fallback behavior, full access-token service startup, original IPC transactions, native-board operation or a HarmonyOS desktop. A separate 008 experiment tests the original `BinderConnector` dependency closure and driver negotiation; its preparation is not itself runtime evidence.
