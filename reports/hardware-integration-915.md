# Experiment 915: GPU-rendered initialization reaches device attestation

## Verified outcome

- Native ARM/KVM, 1920×1080, VirGL → host FD690, no physical viewer.
- Same immutable payload-913 and graphics libraries as experiment 914. Only normal QEMU user-mode networking was added, without forwarded ports.
- Actual framebuffer screenshots show language, region, quick setup, agreement, privacy, activation progress, then the activation error page. **No desktop has been verified.**
- Normal initialization agreements were explicitly authorized by the user; no account login, certificate fabrication, activation-state edits or trust-database changes were performed.

## Current blocker

`next-experiment/run-915/network-diagnostic.txt` contains strings extracted from persisted binary logs, not a complete native log decode:

- Guest Ethernet/network capabilities and successful DNS resolution.
- Cloud challenge response followed by device-login error `1003300005`, `Failed to attest ids`.
- ActivationLockInfoOperator response: `{"resultCode":2,"resultDesc":"socIdCert is empty."}`.
- Normal activation retries end at the error page shown in `run-915/activation-settled.png`.

The visible generic connection error therefore does not establish a DNS outage. The evidence points to missing device-attestation material in this virtual environment. Repeated rendering changes or additional boots do not supply a legitimate device certificate. Further progress requires a vendor-supported virtual/test-device provisioning path or an officially supported image that does not require this physical-device credential; do not copy another device's identity or forge success.

## Graphics work already validated

- Actual OHOS EGL frontend and private Mesa report `virgl (FD690)` with correct GPU pixel readback.
- Typed GBM allocation passes CPU→GPU flush and GPU→CPU invalidation tests at 13×7 and 1920×1080.
- NativeWindow bridge fixture passes orientation, format, resizing, pack/PBO/FBO state, failure recovery and lifetime checks.
- Full-system RenderService now imports native buffers and presents real 1080p initialization pages.
- This path still uses GPU readback and CPU copying; it is not zero-copy scanout. Future graphics work should target fence/cache correctness under sustained load, reduced copies, display capture integration and reproducible packaging. None of that substitutes for device attestation or proves desktop success.

## Lifecycle

Guest status was `running`; graceful QMP `quit` was accepted. Final original-image integrity checks and per-run userdata deletion must be recorded only after the runner finishes. Physical screen remains intentionally off.
