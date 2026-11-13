# 896: RenderService software-driver overrides found

Both primary and render DRM nodes opened successfully in RenderService, but independent `gbm_create_device` calls returned NULL on both. This does not support a primary-node authentication explanation. Standalone direct bridge and unchanged product EGL frontend still passed real VirGL (FD690) green-pixel readback.

Read-only extraction of original `/etc/init/graphic.cfg` revealed RenderService-specific settings `LIBGL_ALWAYS_SOFTWARE=true`, `GALLIUM_DRIVER=softpipe`, and `MESA_LOADER_DRIVER_OVERRIDE=softpipe`. The experimental Mesa build contains VirGL, not softpipe. Other processes do not necessarily inherit these per-service overrides.

Fresh payload 897 removes only those three environment entries in a RAM-bound, read-only configuration copy. Jobs, service identity, groups, capabilities, permissions, restart policy, preload and all other environment entries remain unchanged. No original disk is modified. This is a hypothesis test; runtime success and desktop presentation remain unverified.

Payload SHA-256: `20f3fd38d31afcf158a6756ead3774df93b23e99482cbffb6723dd4ef5875848`.

Evidence: `next-experiment/diagnostic-896.txt`, `next-experiment/gpu-runtime-883/original-graphic.cfg`. Post-run integrity is recorded separately by the runner.
