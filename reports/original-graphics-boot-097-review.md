# Original graphical boot 097 — lock screen and slow frame processing

## Independently verified results

`original-graphics-boot-097-independent.json` was produced once after run 097 completed. Serial SHA-256: `b828d6678450dff003a262ef4af200f8643867e5cc53b38cb1d3168efca73ee9`.

- All 12 injected provider files, genuine ashmem, configuration query helper, initrd, virtual kernel and three original SDK images passed the full independent checks. The inherited checks also preserve the 378 earlier native evidence files, private 8 GiB test volume and original service identities.
- No Foundation critical fault or guest reboot was observed within the 660-second bound. This does not establish continued stability outside that window.
- Nine actual QMP captures were independently checked for PPM/PNG pixel identity. The 540-second capture contains **50,000 nonblack pixels** at 1280×800, pixel SHA-256 `7018e0bc479e37e29dc41bb3683e851ccd30e1a69e70c1caaf44798f2565a402`. Visual inspection confirms the genuine lock/login screen: clock, user avatar, `user`, and the original Chinese password-required message. It is not an unlocked desktop or physical MateBook output.
- Captures at 120, 360, 480, 570, 600, 620, 640 and 650 seconds are black. Neither a black capture nor the lock-screen capture alone determines whether the later display state is a rendering failure or original power-management behavior.

## Original RenderService evidence

Original RenderService PID 1253 HiLog queries at samples 41, 49 and 61 exited normally. Actual logs include:

- Screen 0 active mode 1280×800 at 75 Hz.
- `CreateNodeAndSurface` code-3 requests completing after 1049, 2118 and 4314 ms, and genuine SceneBoard render-node creation. These are observed delays, not proof of a permanent deadlock.
- `RenderFrame task too long` at 6162, 7442 and 4363 ms; compositor tasks taking roughly 1.4–3.3 seconds.
- The original watchdog reporting RenderService's `vSyncTask` blocked for five seconds and generating its own stack report. Protection remains enabled; no timeout or authentication check was removed.

The environment uses ARM64 TCG and real software Mesa. These measurements justify investigating performance, but they do not isolate a single slow operation or prove that performance explains every black capture.

## Power-query limits and next diagnostic

Nine complete parameter-query pairs were parsed. Their original CLI output reports error 106 for `startup.device.ctl` / `ohos.startup.powerctrl`, despite zero process exit status. No reboot-request value was established; one expected pair was not captured as a complete parseable record. No parameter was written.

Fresh candidate **098** adds only genuine `hilog -z 400 -P <actual powermgr PID>` queries at samples 41, 49 and 61. Discovery occurs before the verbose process filter; it does not add repeated power-service memory-map dumps. Existing graphics, providers, original power policy, sandbox, user identities, login checks and 660-second deadline remain unchanged. Its purpose is to distinguish observed original display-power transitions from rendering failures, not to disable automatic screen-off.

Offline gates: 098 **3 passed**, parent 097 **3 passed**. Preparation succeeded once; runtime and independent verification remain pending at this report's creation.

All work is local isolated WSL/QEMU testing. No MateBook/Ubuntu boot, host security, automatic screen-off or physical-display changes were made. Completed numbered operations and evidence were not rerun or overwritten; no downloads, subagents, commits or external publication were performed.
