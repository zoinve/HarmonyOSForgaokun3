# GPU dispatch diagnostic 888

887 completed with all original image integrity checks passing. Its stopped experimental userdata was deleted after verifying both results, no QEMU/open file descriptors, and the protected original userdata hash before and after deletion.

888 loaded the expected Mesa/GBM/bridge libraries into RenderService. However, both standalone probes failed at `exec` with `Permission denied` (exit 125); no GL dispatch result was obtained. The actual initramfs contained the diagnostic executable as mode 0444, despite the compiled file being 0755. Its builder reused the library-only archive routine.

A new archive-permission regression check reproduces this failure on the immutable 888 payload. Fresh payload 889 uses identical files/binaries and changes only the probe archive mode to executable; the regression check passes. SHA-256: `35a7558dbe1b93abf80940199b04bf3a8e963ade35ae9d6db88eea57d740b672`.

888 was stopped gracefully through QMP. Post-run integrity results are recorded separately on completion. No desktop or full-system hardware-rendered frame has been verified. Original OHOS EGL/GLES frontends remain unchanged; no activation, account, trust or watchdog bypass was introduced.
