# Original graphical boot 096 — genuine lock screen, remaining freezes/reboot

## Independently verified image

`original-graphics-boot-096-independent.json` verifies an actual QEMU scanout at elapsed 600.0182 s: **1280×800, 49,101 nonblack pixels, 921 colors**. Independent PPM/PNG decoding and CRC checks agree. Visual inspection of `baremetal-sdk-original-init-qemu-096/frame-600.png` shows the genuine lock/login screen: clock/date, user avatar, `user`, and “未登录用户需要输入密码”.

- RGB SHA-256: `3ba4d8af2e43386d78dcfca33b5a98f87c98a474d5a9c745295cccf1b84f1dfb`.
- PNG SHA-256: `1c9e5ac083904bee3b02cf34bcf7313bbe63e03d1b00f13321765d03e6970860`.
- Captures at 120, 360, 480 and 650 s are black. One visible frame does **not** establish stable interactive operation, an unlocked desktop, or physical MateBook scanout. Authentication was not bypassed.

## Genuine runtime issues, not inferred causes

Original SceneBoard HiLog queries at samples 41/49/61 completed normally (PIDs 3093/3093/4184). Genuine app-freeze evidence was recovered read-only from the retained disposable test data, without mounting, repairing or rerunning it; see `original-sceneboard-freezes-096/result.json` and its four original log files. Original scratch SHA-256 remained `cdb54c9d7292f08c59900c4b6afbf1e103ae3bf651b0ef3b39c474e603f60523` before and after extraction.

The PID 4184 freeze shows its main thread waiting for a SceneSession worker. Worker TID 4497 is inside genuine Binder `RSClientToRenderConnectionProxy::CreateNodeAndSurface`. The sample-61 Binder snapshot independently captures transaction **119883**, code 3, from **4184:4497 to RenderService 1289:1482**, pending approximately 4.7 s. The matching server thread is in a futex wait. This identifies a captured request boundary; it does **not** identify the exact userspace lock, establish permanent deadlock, or prove every freeze has that cause. Separate long requests to EngineService are not attributed to RenderService.

The original guest requests power control through Foundation near 649.13 s and reboots at 650.0796 s. The parameter values were not captured. Watchdog service failures also appear, but the precise reboot cause is **unknown**; freeze/watchdog protections were not disabled. No Foundation critical fault was observed.

## Preservation and scope

- All 72 observed SELinux samples are permissive (`0`), with original policy support/audits retained.
- Actual sampled root flags remain `5` (read-only, nodev); `/mnt` flags `4098` (writable, nosuid, relatime).
- Independent checks passed for all 12 injected provider ELFs, genuine ashmem, query helper, initrd, virtual kernel, all three original SDK images, the private 8 GiB disk-backed test volume and 378 prior native evidence files.
- Serial SHA-256: `dc176b3a073f8b51622008fe3c610a92ce47ef1c7ff169f76ccf3da8247d3946`.
- Work remained isolated WSL/QEMU testing. No MateBook/Ubuntu boot, host security or automatic screen-off changes; no original service identities, permissions, profiles or authentication checks were bypassed. All three reference projects remain applicable.

## Fresh 097 diagnostic

Same original system/providers/kernel/resources and 660 s bound. Adds only genuine RenderService `hilog -z 400 -P <actual PID>` queries and read-only original `param get` requests for `startup.device.ctl` and `ohos.startup.powerctrl`; actual responses/timeouts remain authoritative. Extra virtual scanout samples at 540/570/620/640 s may show the transition more clearly; they are not synthetic frames.

Offline checks: new 097 suite **3 passed**, parent 096 suite **2 passed**. Preparation completed once: init 853,920 bytes, SHA-256 `822eb585b7795f9f94db9188de7fb3a74cc3448a39c30a9e3c6b39d1496ac029`; policy and graphics config hashes unchanged. Runtime and independent verification are pending at report creation. Completed 096 and its extraction/verifier were not rerun.
