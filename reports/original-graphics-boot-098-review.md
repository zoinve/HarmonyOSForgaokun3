# Original graphical boot 098 — power observation and real lockscreen

## Independently verified result

`original-graphics-boot-098-independent.json` records successful independent verification of all 12 provider ELFs, ashmem, the query helper, initrd, kernel, three unchanged original SDK images, retained private 8 GiB test volume and 378 prior native evidence files. Serial SHA-256: `5806adc8ad672b5172ece52a7235a09e6c37454979b3bfb20bb1a5c90bbc1c3e`. All 72 observed SELinux samples are permissive, not disabled. Completed run/preparation/verifier were not rerun.

Nine real 1280×800 QMP captures passed independent PPM/PNG/raw-pixel checks. The 540-second frame has 50,000 nonblack pixels, pixel SHA-256 `7018e0bc479e37e29dc41bb3683e851ccd30e1a69e70c1caaf44798f2565a402`. Visual inspection confirms the original login/lockscreen, clock 08:08, user avatar and password prompt. Other captured frames are black. This is not an unlocked desktop, verified interaction or physical MateBook scanout.

No Foundation critical fault was observed; an original guest reboot was observed. Its precise cause remains unverified. Authentication, freeze/watchdog protections and original power policy remain unchanged.

## What the power logs establish — and do not

All three original HiLog queries of actual powermgr PID 666 (samples 41, 49, 61) exited normally. Captured genuine messages include `bootevent not fired!`, running-lock HDI `HoldRunningLockExt_` errors, battery configuration errors and thermal subscriptions. The excerpts do **not** contain a clear display-off transition explaining the black QMP captures. Failed running-lock requests are not proof that automatic screen-off caused every black frame, and no success reply or missing power backend was fabricated.

Separately, the retained original 097 system-freeze report establishes that the RS main thread waits in `RSDrawFrame::PostAndWait()`, while its render thread progresses through the real softpipe TGSI shader interpreter and EGL frame copy. See `original-render-freeze-097/review.md` and its hash-verified raw reports. This supports a software-rendering workload bottleneck in the TCG test, not a native Adreno performance conclusion.

## Fresh 099 controlled comparison

099 requests only a smaller **virtual hardware** display, 800×600 instead of 1280×800, using genuine QEMU `virtio-gpu-device` properties. It reuses the exact prepared 098 guest, original services/policy/identities, providers, kernel, disk capacity, 660-second deadline and capture schedule. There is no new bootstrap preparation or original resolution-property injection. The verifier requires the actual initrd hash to equal 098, retains all full-artifact and lossless-pixel checks, and checks actual captured dimensions rather than assuming the request worked.

Offline tests: new 099 suite **2 passed**, parent 098 suite **3 passed**, after missing implementation was first observed to fail. Runtime and its independent verification are pending at report creation. Fewer pixels are a diagnostic comparison, not a claim to have fixed the physical port or bypassed a freeze guard.

Everything remains isolated local WSL/QEMU work. No MateBook SSH, Ubuntu boot/security/screen-off changes, original SDK image writes, identity changes, authentication bypass, downloads, subagents or commits were performed.
