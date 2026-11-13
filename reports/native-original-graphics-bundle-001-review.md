# Native original-graphics candidate 001 — inert staging, not a boot result

## Outcome

Prepared and staged an independent **Freedreno / MSM** candidate for the original
HarmonyOS graphics services. It is **not** the VirtIO/QEMU graphics package, a
replacement RenderService, a desktop-success claim, or a new private-method trial.
No target library was executed, no service was started and no reboot was requested.

- WSL build: `/home/zoinve/harmony-virgl-883/native-original-graphics-bundle-001`.
- MateBook staging:
  `/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-bundle-001`.
- Twelve regular ELF files, 20,955,697 bytes, plus three relative GLES aliases.
- Evidence: `reports/native-original-graphics-bundle-001/`.

## Implementation and checks

`next-experiment/build-native-original-graphics-bundle-001.py` refuses to overwrite
numbered output. It uses the existing pinned Mesa 25.0.1 Freedreno/MSM build 003,
not the prefix's VirtIO gallium. Its six Mesa files are checked against build 003's
manifest. The private NDK runtime stays alongside Mesa; platform `libc++.so` is
neither copied nor replaced.

The reference HarmonyMac EGL bridge is compiled with the platform C++ toolchain.
The only source adaptation is its absolute Mesa library path. Unmodified reference
composer/allocator providers and their recorded DRM dependency come from provider
002. Original SDK images and all recorded source files were rehashed unchanged.

The actual compiled GBM backend directory is included at
`/system/lib64/lab-freedreno003/gbm`; no fake successful EGL return or fallback
software-rendering alias was introduced. Static dependency closure allows only the
original target's `libc.so`, `libc++.so`, and `libbuffer_handle.z.so` as external
dependencies. This does **not** establish runtime namespace or ABI compatibility.

`next-experiment/test-native-original-graphics-bundle-001.py` first failed because
the candidate did not exist, then passed after build. Independent checks cover
all twelve hashes, ELF AArch64/musl dependencies, six original Mesa hashes, GBM
backend location, platform C++ ABI, private runtime and contained GLES aliases.
Four disposable-copy negative cases were rejected: missing GBM backend, missing
private runtime, wrong gallium driver, and overwriting platform C++ runtime.
No historical operational experiment was rerun; this workspace has no unified
safe test runner.

An initial negative-test harness run surfaced a FileNotFoundError for the missing
private runtime. The checker now asserts file presence explicitly; all four cases
subsequently produced the intended rejection. Only disposable copies were mutated.

## Real machine safety evidence

Read-only preflight is
`reports/native-original-graphics-preflight-20261112-host.json`.
The physical board has MSM DRM, a connected 1600x2560 DSI panel, and the existing
Ubuntu kernel `7.1.0-rc3-gaokun3+`. Panel disablement is consistent with the retained
automatic screen-off policy; this is not a screen-on result.

After staging, all twelve file hashes and three aliases matched on the MateBook.
All 82 baseline EFI files matched, Ubuntu's persistent default was unchanged,
the automatic screen-off timer remained active and the boot ID was unchanged:
`6b46894a-8b4b-49a4-bf71-5a903d6b3d95`.

The first verification ran as the normal SSH user and could not read
`/boot/efi/tcblaunch.exe`. Transfer had already finished and was **not repeated**.
Only the read-only verification was rerun with `sudo -n`; it passed. This is
recorded in `stage-result.json`. No EFI files were written.

## Main-path continuation and remaining gates

The next integration is a separately numbered **native original-init boot
candidate**, with recovery/watchdog and read-only original-image attachment.
The existing original-init bootstrap is QEMU-specific (`dummy-virt`, `/dev/vd*`)
and cannot simply be executed inside Ubuntu. The staged directory is not an
installed `/system` or `/vendor` and is not yet consumed by a boot candidate.

Ubuntu currently has no active SELinux LSM despite kernel SELinux support. Do not
load the target policy into Ubuntu or call the host permissive. The HarmonyOS
target may use the already-authorized permissive mode with policy/audit evidence.
Preserve original service credentials, Binder/HDF configuration and platform ABI.

The reference bridge opens a primary DRM card and can acquire/drop DRM master;
therefore it was deliberately **not** run in Ubuntu as a render-only probe.
Physical display ownership and original-service startup belong in the isolated
target/recovery path, not the completed native trial 012 sandbox.

All three references remain relevant: the L410 Adaptations original service/HDI
chain, Linux Compatibility Platform's later compatibility layer, and HarmonyMac's
real DRM/EGL provider. Revisions and source entry points remain pinned in
`reports/reference-three-projects-001.md`.

No original RenderService startup, HDF display completion, modeset, desktop, or
physical screen-on success has been verified by this candidate. Concurrent
original-graphics 058/059 work and all prior numbered evidence were left untouched.
