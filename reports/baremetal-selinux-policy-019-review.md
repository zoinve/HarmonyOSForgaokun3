# Original production SELinux policy: isolated enforcing test

## Verified result

`baremetal-selinux-qemu-019/result.json`, serial log and independent verification record show:

- The unchanged SDK vendor production `policy.31` (3,170,670 bytes, SHA-256 `3119d6aae760a6d692459ce9d83aeb6354301bc1fb9b084d005664f6a543d8e5`) was accepted by the identity candidate's console-test kernel.
- SELinux was active and enforcing both before and after load. The command line retains every baseline LSM, adds SELinux and explicitly selects `enforcing=1`; neither policy nor enforcing controls were weakened.
- A malformed policy was rejected. The original policy authorized PID1's transition from kernel to `u:r:init:s0`.
- Console labelling uses the original SDK `/dev/console` context, `u:object_r:dev_console_file:s0`. A RAM tmpfs `/dev` and post-load label restoration permit normal init-console output. The retained, deliberately wrong rootfs console descriptor is denied with `EACCES` and an enforcing AVC.
- Serial SHA-256: `40e39180b870a95c1f243e6e9a7cbf1adbe3cd02a4c54c9756ed9ced7253fc62`. Independent checks matched local/WSL result and serial bytes, all prepared file hashes/sizes and the actual kernel hash.

The exact reused test kernel SHA-256 remains `130f30abc9c9fc8faf1fb84bec268a1cde10fabdc3c93839250f347924f27bad`. Native candidate configuration, critical source files and test kernel/configuration remained unchanged. The VM had no storage, network or GPU devices. No board reboot, installation, original-image modification or boot-default change occurred.

## Investigation and failed fixtures retained

013 found that `CONFIG_SECURITY_SELINUX=y` was insufficient: the baseline `CONFIG_LSM` omitted SELinux. Earlier successful IPC tests therefore did not demonstrate enforcing-policy compatibility. 014 activated SELinux but correctly refused its development-mode permissive default. 015 added explicit enforcing mode and loaded production policy, but rootfs-console denials prevented a completion marker.

016 confirmed the policy-authorized init transition, but pre-load xattrs did not give the live rootfs console the required post-load label. 017's attempted restoration was correctly denied: production policy does not grant init `relabelfrom` for rootfs character devices. The original CIL instead explicitly grants this operation for tmpfs character devices. 018 corrected the RAM device filesystem but exposed an incorrect negative-test assumption: writing its still-generic tmpfs console as kernel was allowed. That failure was not a policy failure.

019 keeps the valid RAM console and tests denial on the deliberately retained rootfs descriptor instead. All failed run reports remain failures, with their logs unchanged. The final PASS's `errno=13` is the retained expected negative-test errno, not a failed completion.

Host compilation and actual non-PID1 refusal were independently exercised for generated 016, 017, 018 and 019 probes. This is a targeted safety check, not a repository-wide test-suite claim.

## Limits and next work

This verifies policy loading, enforcing mode, authorized bootstrap transition, console restoration and a real negative authorization path. It does not yet combine enforcing policy with the earlier original-SDK Binder/token transaction tests, run samgr/access-token services, verify all policy paths on Linux 7.1 or boot HarmonyOS on the board. New kernel classes/permissions absent from the original policy remain denied, as the log explicitly reports.

The native candidate still needs a deliberate active/enforcing SELinux boot configuration and a correctly labelled userspace before any full SDK boot can be claimed. No inactive/permissive baseline result is substituted for that work.
