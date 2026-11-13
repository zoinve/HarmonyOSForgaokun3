# 895: backend loads, RenderService GBM creation still fails

The bounded diagnostic completed (`next-experiment/diagnostic-895.txt`). RenderService has matching real/effective IDs (UID 1003, GID 1000), expected GBM backend environment, and accessible DRM nodes. Explicit loading of the actual `dri_gbm.so` returned a non-null handle and its `gbmint_get_backend` symbol. The accompanying `tls/dri_gbm.so` error string is not evidence that this successful load failed; it may be retained from an earlier candidate lookup.

RenderService's original primary-node `gbm_create_device` still returns null. Both standalone bridge and unchanged product frontend tests continue to pass real VirGL (FD690) green-pixel readback. No desktop or full-system scanout is verified.

Fresh immutable payload 896 adds only a diagnostic comparison: after the original GBM failure, open `/dev/dri/renderD128`, try creating a separate GBM device, log the result, and destroy/close only these diagnostic resources. It preserves the original EGL result and permissions. This tests a primary-node versus render-node difference without assuming an authorization failure.

Payload SHA-256: `4f9dc76d8558afcb257bf2015f72621936c5b39ee23807473430f196fd3c2550`. Actual archive executable-mode check passed. Experiment 895 was gracefully stopped; post-run integrity checks and userdata cleanup are recorded separately.
