# Original SDK BinderConnector regression 008

The original `libipc_common.z.so` and its recursively extracted, unmodified SDK dependencies ran with the original SDK loader in diskless QEMU against the identity-patched kernel. No shared-library replacement or successful unsupported-ioctl stub was used.

The actual run reported:

```
IPC008_PASS protocol_accepted=1 access_token=1 real_pid=1 unsupported_features=0 task_tokens_preserved=1 transactions_not_tested=1
SDK008_PASS checks=19 original_library=1 spm_unsupported_honestly=1 services_not_tested=1
```

`BinderConnector::GetInstance()` opened the isolated guest's real Binder device. The original connector accepted protocol version 8, observed token/real-PID features, did not advertise refresh/calling-user-info support, and returned the current task's authentic self/first-caller token values. Calls use exported nonvirtual methods and an opaque instance pointer; the test does not fabricate C++ object layouts.

The prior raw synchronous, one-way and nested Binder regressions remained in the same run and passed. They are not original-library IPC transactions. Original-library connector negotiation, token APIs and raw driver transaction tests are separate evidence layers; full service startup and original IPC transaction dispatch remain unverified.

Independent verification checked all 16 packaged files' sizes and hashes, local/WSL result and serial-log equality, and failure/panic absence. Serial SHA-256: `740d7681e14a83442c7daf0fce7ae411cd5867352e28276c2eca7dc2cd8c4046`.

The exact 002 test kernel was reused unchanged. No physical-board boot, disk/network/GPU attachment, Ubuntu configuration change or SDK image modification occurred. The following native preparation uses a fresh inert initramfs base with all 391 modules from the identity-patched build; it is not evidence of a physical-board ABI pass or HarmonyOS desktop readiness.
