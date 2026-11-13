# Headless 878: reduced-rendering comparison

Same native ARM/KVM kernel and read-only diagnostic payload as 877; fresh independent userdata. Only the framebuffer changed from 1920×1080 to 960×540. Physical screen stayed off.

Actual keyboard navigation and screenshots:

1. Welcome → language (`language-lowres-878.png`).
2. Language → region (`region-lowres-878.png`).
3. Region → **快速启用**, successfully displaying a focused **跳过** button after 45 seconds (`quicksetup-lowres-878.png`). The corresponding 1080p transition in 877 remained stuck for minutes.
4. Normal **跳过** → **协议与声明**, displaying focused **同意并继续** (`after-quickskip-878.png`). No agreement was accepted.

This supports excessive software rendering work as an important contributor, but does not identify a precise shader defect or establish that every stall is resolved. The low-resolution page layout is visibly clipped, so this is not a suitable final UI configuration.

Next progress requires reviewing/authorizing the software agreement, rather than fabricating an OOBE completion flag. No activation, account, trust or agreement database was edited. No genuine desktop has been verified; a success-conditioned GPU plan is not yet delivered.

Storage after this fresh userdata copy: approximately 3.5 GiB free (97% used). Do not start another full-copy experiment without addressing capacity. Existing experiment data is retained.

877 post-run integrity checks completed successfully: original read-only inputs unchanged; protected original userdata unchanged. 878 post-run checks are recorded separately when its bounded runner completes.
