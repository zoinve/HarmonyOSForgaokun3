# OHOS Freedreno: GBM / DMA-BUF evidence 001

## Verified outcome

An OHOS AArch64 executable, original SDK runtime loader and independently built Mesa 25.0.1 Freedreno libraries ran on the MateBook's **Ubuntu kernel** `7.1.0-rc3-gaokun3+`. The hardware renderer was `FD690`. This is not a HarmonyOS desktop or native HarmonyOS boot result.

The real GPU test completed these steps without opening a display window or obtaining DRM master:

1. Open `/dev/dri/renderD128` and create a GBM device.
2. Allocate a 16×16, single-plane ARGB8888 buffer with explicit linear modifier. Actual stride was **256 bytes**, offset 0, modifier 0.
3. Export a DMA-BUF FD and import it as an EGL image; attach it to a complete GLES framebuffer.
4. Render the existing red triangle over a blue background. GLES readback returned center `255,0,0,255` and corner `0,0,255,255`.
5. Independently open the render node again, create a second GBM device and import the exported DMA-BUF there.
6. Map that imported buffer for CPU reading. After interpreting ARGB8888's little-endian BGRA bytes, the mapped center at (8,8) and background at (0,8) were again the expected opaque red and blue.

The process exited 0 in approximately 164 ms. The captured kernel log had no new lines. GPU completion in this version uses `glFinish`; native-fence synchronization is a separate next test, not established by this result.

## Artifacts and checks

- `baremetal-freedreno-dmabuf-package-001/package.json`: nine AArch64 ELF files, dependency and strong dynamic-symbol closure checked; includes the matching dynamically loaded `gbm/dri_gbm.so` backend.
- Package archive: 6,402,954 bytes, SHA-256 `5954cbce1d2ac3c5f8ba62272b6bbe3fc850a37d73769d9e6504add8057aa37d`.
- `baremetal-freedreno-dmabuf-run-001/result.json`: full stdout/stderr, security admission, live pre-start unit properties, boot and preservation checks.
- `baremetal-freedreno-dmabuf-run-001/independent-verification.json`: all nine deployed file sizes/hashes and the known relative libc symlink checked independently; unchanged boot ID; GDM already logically off using a verifier that refuses all display setters; Ubuntu default and empty one-shot preserved; obsolete diagnostic entries still absent.
- Real native C metadata-policy tests were observed failing before the helper existed, then passed. They reject invalid FD, dimensions, plane count, stride, offset and modifier. They do not constitute GPU evidence themselves.

## Isolation and limits

Live captured sandbox: UID 1001, supplementary render group, no capabilities, no-new-privileges, device policy closed with only renderD128 allowed, card0 admission denied, read-only system/home isolation, private networking/tmp, AF_UNIX only, 45-second runtime limit, 512 MiB memory and 32 tasks. No Ubuntu libraries, SDK images, kernel, authentication state, boot entries or default were replaced. The private test bundle is retained under `/var/lib/harmony-lab-freedreno-dmabuf-001`.

Mesa still warns that `os_same_file_description` cannot determine DRM FD identity, this time reporting `No such file or directory`, and uses its existing fallback. Successful independent-open buffer sharing is evidence for this tested path, **not** proof that the fallback is safe for every multi-FD workload. No security restriction was relaxed to suppress it.

Not tested: cross-process buffer passing, non-linear/compressed modifiers, multiple planes/formats, compositor scanout, physical display or touch, long-duration stress, native HarmonyOS graphics integration. The previously documented Binder/access-token/SPM ABI blockers remain unchanged.
