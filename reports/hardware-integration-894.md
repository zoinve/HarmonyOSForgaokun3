# 894: RenderService fails at GBM device creation

- Same native ARM/KVM, 1080p VirGL setup and RAM-only graphics overlay.
- RenderService PID 1330 opens display DRM successfully (FDs 12 and 18), but `gbm_create_device` returns null. Subsequent EGL display/config/context arguments are null.
- Its namespace contains card0 and renderD128, both mode 0666, owner 0, group 1003. A device-node access problem has not been established.
- SceneBoard obtains a GBM device and real EGL contexts. Both standalone tests, including the unchanged product EGL frontend, report `virgl (FD690)` and correct green pixel readback.
- Mesa's loader uses `GBM_BACKENDS_PATH` for matching real/effective IDs; the recorded RenderService IDs match. A secure-environment explanation is not established.
- No genuine desktop or working full-system presentation has been verified.

Evidence: `next-experiment/diagnostic-894.txt`.

Fresh diagnostic payload 895 records process IDs, backend environment, and the explicit backend `dlopen`/symbol error after GBM failure. It does not change EGL return values, service identities, drawing, or protections. SHA-256: `b4d428d9c4887cf6650f82d0de78a7c7eb982deb03d9b72af7a985b32b7a50b0`. Actual archive executable-mode check passed.

894 was stopped with QMP quit; final integrity results are reported separately after the runner completes.
