# 914: normal initialization reaches a genuine network requirement

Native ARM/KVM, VirGL/FD690, 1920×1080, original OHOS EGL/GLES frontends, RAM-only graphics adaptations. Physical panel stayed off. No guest NIC was attached in this experiment.

Actual framebuffer images were read after each normal keyboard action:

- Language → region → quick setup → skip → software agreement.
- Authorized ordinary agreement acceptance → privacy page (`run-914/agreement-next.png`).
- Tab visibly focused privacy Continue (`privacy-focus.png`), then Enter opened the network error (`privacy-next.png`): **网络未连接，请检查网络设置**.

Read-only extraction of current guest logs identifies `FindServiceOOBEActivationLock`; its normal network check returned false. These binary log strings are partial NUL-separated extraction, not a complete native decode. No activation success is inferred from internal event names or result codes. No activation, account, trust or readiness database was modified.

Next bounded comparison adds only normal outbound QEMU user networking with a virtio NIC and no port forwards. Graphics/payload remain identical. Existing default remains `-nic none`. Configuration test observed missing-option failure before implementation, then passed alongside six existing launcher checks.

**No genuine desktop yet.** Post-run original-image integrity and per-userdata cleanup are recorded separately after the runner finishes.
