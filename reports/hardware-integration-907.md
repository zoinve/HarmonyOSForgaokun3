# 907: RAM allocator integration, no desktop

- Only the vendor buffer VDI was readonly RAM-bound to the independently validated GBM allocator. Original images, service identities and protections were unchanged.
- Standalone allocation through the vendor path now passes both 13×7 and 1920×1080 real VirGL import and exact pixel readback, confirming the bind is visible to that test.
- System presentation did not succeed. QMP reports `no surface`; actual framebuffer extraction shows four Linux boot penguins on black, not HarmonyOS desktop or OOBE. Nonblack pixel count alone was not success evidence.
- Composer snapshot has no client buffer (`client_fd=-1`, dimensions zero), while RenderService repeatedly reports allocator/Bufferqueue errors. Their encoded UUID messages do not establish the precise failing allocation.
- Fresh diagnostic-only payload 908 redirects bounded allocator breadcrumbs to the private RAM trace directory and adds device/export/size-rejection reasons. Allocation policy and rendering binaries otherwise remain unchanged. Payload SHA-256: `6d2ae0982c1e75c68a409c0cc793479315ce483475b65de07e9b4530b72861c1`.
- Actual 908 archive executable-mode test passed. 907 post-run integrity results are recorded separately when available.
