# 908: service allocator fails GBM initialization

- The real allocation calls occur in UID/GID 3041, not in the successful standalone root probe. Its private RAM trace repeatedly records `GBM_DEVICE fd=7 device=0 errno=2`, for both 512×512 and 1920×1080 buffers.
- RenderService requests fail with `GPU898_REQUEST rc=50002000 buffer=0`; no client buffer or genuine desktop is established. The framebuffer still contains boot artwork, not desktop success evidence.
- Independent vendor-path and private-plugin allocations continue to pass real VirGL import and exact pixel readback at 13×7 and 1920×1080. This does not establish equivalent loader environment in the service.
- Fresh diagnostic-only payload 909 records the allocator's actual backend/driver environment and explicit backend `dlopen` result. No permission, identity, allocation-policy or graphics-function return changes were made. SHA-256: `3c630226b9072327a2025bac04df4ba598805a72c2f5a9cca5956f111c063858`.
- The actual 909 archive executable-mode check passed. 908 was gracefully quit; its post-run integrity checks are recorded separately when available.
