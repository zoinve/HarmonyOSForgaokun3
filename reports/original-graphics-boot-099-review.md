# Original graphical boot 099 — smaller virtual display, unchanged guest

## Verified comparison

Only QEMU's virtual display request changed, from 1280×800 to 800×600. Independent verification confirms the actual guest initrd is byte-identical to 098, SHA-256 `020beefb77ebaecaadf88c8b9c30ccc1211e26e0e8ca6a8681a58fb602a4c11e`. Original services, policy, identities, authentication, watchdog/freeze protections, power policy, kernel, providers, disk capacity and 660-second deadline were not changed.

`original-graphics-boot-099-independent.json` verifies all 12 provider ELFs, real ashmem, query helper, initrd, kernel, three original SDK images, retained private 8 GiB volume and 378 previous native evidence files. Serial SHA-256: `d850e2f0ddf3558d499e6e66ed3c0be64a10ca3a2478e8cf23bcd93dde9beacb`. No Foundation critical fault or guest reboot was observed within the bounded run. This is an isolated software-rendered VM, not a physical MateBook display test.

## Actual visible result and limitations

All nine captures are independently checked 800×600 PPM/PNG frames with exact lossless RGB agreement. Frames at 120/360/480/540/570 seconds are black. The 600/620/640/650-second captures each have 480,000 nonblack pixels and show the genuine full-color login/lockscreen with wallpaper, avatar, password prompt and clock. Visual inspection of 600 and 650 confirms the clock advances. Pixel hashes:

- 600: `6bc7ab5358b9aad42ec387fff084633383ab2751a24db3ec7d18099720f58ce0`
- 620/640/650: `defd560f84731b4f17692d65a49c68a7697e511157c9c428f8b8bab142857d5f`

The small display has overlapping UI elements. Original RS logs still include a 5-second watchdog report, a render frame of 8759 ms and other multi-second frames. More visible captures do not establish statistically measured speedup, absence of freezes, interactive operation, an unlocked desktop or complete physical adaptation. No password or other authentication was bypassed.

## Verification correction, not a runtime rerun

The first verifier correctly refused the inherited exact device token `virtio-gpu-device`, because the new real command uses `virtio-gpu-device,xres=800,yres=600`. Its output remains `original-graphics-099-verification-output.txt`. A new regression test failed first, then the not-yet-successful 099 verifier was corrected to require the exact requested device properties. Three offline tests passed; the fresh read-only verification output `original-graphics-099-verification-output-002.txt` succeeded. The VM and all earlier completed operations were not rerun, and raw frames/logs were not rewritten.

## Next: build-only native graphics prerequisite

The genuine RS freeze stacks already identify work in softpipe's shader interpreter and frame copy. Rather than continuing only VM observation, the next isolated build targets the real OHOS-compatible Freedreno backend with **MSM only** for the MateBook's Adreno path. It uses the existing local Mesa source and OHOS toolchain, a fresh build directory, no downloads or installation, explicit `allow-kcmp=enabled`, AArch64 ELF/dependency checks and unchanged-source/old-build guards. No target ELF execution, DRM device access, modesetting, native service deployment or host/native module load is authorized by this build step. Its outcome is pending at report creation.

All three reference projects remain applicable. No MateBook SSH or Ubuntu boot, security, display or automatic-screen-off changes were made.
