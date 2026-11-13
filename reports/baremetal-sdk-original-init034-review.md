# Original SDK PID1 handoff 034

## Purpose

The manual samgr fixture reached the real SDK loader and correct service domain, but did not register a usable Binder context manager. Live samples repeatedly traversed genuine parameter/logging bootstrap code. The original libc implements parameter-workspace initialization; invoking its internal initialization with guessed arguments would not reproduce the original init lifecycle.

This experiment instead hands PID1 to the **unmodified original `/system/bin/init --second-stage`**. It is a bounded diagnostic, not a claim that HarmonyOS or any service is ready.

## Isolation

- QEMU virt/TCG only; no physical MateBook reboot, network, or GPU.
- All three original `system.img`, `vendor.img`, and `sys_prod.img` drives are attached `readonly=on`. Guest mounts require block-level read-only status, ext4 read-only and `noload`.
- `/data` is a 256 MiB RAM filesystem. No original userdata image is attached.
- Original `/usr` system layout and RAM symlinks expose the original library-search configuration. No library replacements, invented parameters, token data, or substitute Binder manager.
- Explicit `enforcing=1` and the full existing LSM list plus SELinux. The handoff helper requires active enforcing mode before exec. It does **not** preload or modify policy, switch domains, or change enforcement: original init must perform its own initialization. Enforcement after handoff remains unverified until runtime evidence exists.
- The host terminates observation after 60 seconds and records serial output even on failure. Before/after whole-image hashes and kernel/config/critical-source guards are retained in the numbered result.

## Preparation verified

`test-baremetal-sdk-original-init-034.py` compiled the actual C helper with warnings-as-errors and verified non-PID1 refusal (77), before any mount/device action. All three Python sources and both generated payloads compile. The actual token-driver host regression harness passed its four groups: unsupported requests, identity authorization, permission handling, and initialization failure cleanup.

Prepared static ARM64 helper: 777,672 bytes, SHA-256 `3bc802aa42610b86003563da65d8aa04b4b7f32d187b3d724a0582a8e7750900`. Source SHA-256 `b73ccc943f3003f377d98c563a2163517b89fa47cc975ee89ad34d8ab301fbe1`.

The extracted original production policy remains 3,170,670 bytes, SHA-256 `3119d6aae760a6d692459ce9d83aeb6354301bc1fb9b084d005664f6a543d8e5`. It is a preservation reference; the handoff initramfs does not load this extracted copy.

## Runtime

Started once; result pending at the time this section was written. Merely reaching the handoff marker, surviving the observation window, or a zero QEMU exit code will **not** be treated as service readiness, successful policy initialization, or desktop success.

### Actual 034 result

The observation finished in about 1.07 seconds with `runtime_verified=false` and `services_ready=false`. The helper reached its handoff attempt, but `execve` returned ENOENT. Serial capacity evidence identifies the fixture error: `vda` was the 1,000 MiB sys_prod image, `vdb` was vendor, and `vdc` was the 3.42 GiB system image. The initial helper incorrectly assumed system was `vda`.

All three **whole original image** hashes, the test kernel/config, native config, and guarded critical sources were unchanged. No original init success or post-handoff policy verification is claimed.

Fresh 035 artifacts correct discovery only: explicit virtio device serials, exact sector-capacity checks, and rejection of ambiguous or missing identities. The actual C selection function passed controlled reversed-enumeration, wrong-capacity, missing-serial and duplicate-serial tests. The generated 035 helper also passed warnings-as-errors compilation and real non-PID1 refusal. No 034 artifact or failed result was overwritten.

Independent 034 verification subsequently passed: both prepared files, all three whole original images, the actual test kernel, and local/WSL result and serial byte equality. The verified serial SHA-256 is `75652e0314fe6d89da95701e8b02543446842f6044d6383976be05df7b954615`. The ENOENT failure and false readiness flags were explicitly verified, not reclassified as success.
