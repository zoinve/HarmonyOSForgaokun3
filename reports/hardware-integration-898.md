# GPU integration 898: window submission succeeds, display remains black

The native ARM/KVM run preserved the original OHOS frontends and service identities. Both standalone EGL paths still report `virgl (FD690)` and pass real green-pixel readback.

Actual RenderService bridge traces show repeated successful 1920×1080 NativeWindow buffer requests, GPU-to-buffer copies (format 12), queue flushes, and Mesa swaps. This verifies those operations' return values, not that the final display contains the UI.

At the 120-second observation, the real fbdev buffer contained zero nonblack pixels. DRM state still selected framebuffer 44 allocated by fbcon. No genuine desktop has been observed. The physical screen remains off.

Fresh diagnostic payload 899 adds read-only inspection of the preserved Composer binary's client-buffer state and samples its buffer file descriptor. Rendering libraries and functional behavior are unchanged. Its archive SHA-256 is `e5042f44a266262bb2ed373b81fac77fac127640a8bef9c4c81765bf48b88192`; the actual archive executable-mode check passes. Post-run integrity is recorded separately.
