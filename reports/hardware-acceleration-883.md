# VirGL hardware acceleration: verified boundaries

## Results

- Host: EL2 kernel, working KVM, Adreno exposed by Freedreno as `FD690`.
- A root, headless EGL/GLES probe created a real GPU context and read back its clear color. The unprivileged SSH user's fallback renderer was llvmpipe; that fallback is **not** hardware acceleration.
- Matching QEMU 10.2.1 OpenGL modules and libvirglrenderer 1.2.0 were downloaded, package hashes checked, and extracted into an isolated directory. No host package upgrade or GPU passthrough was performed.
- A diskless, native ARM/KVM boot using the retained guest kernel negotiated `virgl`, `context_init`, and two capsets. The guest exposed `/dev/dri/renderD128`.
- **HarmonyOS userspace hardware rendering and an accelerated desktop are not yet verified.** The retained software Mesa library exposes softpipe; a compatible OHOS-native VirGL userspace is the next dependency.

## Reproduction evidence

Remote directory: `/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883`.

- `packages.json`: isolated module package identities and hashes.
- `qemu-host-probe.stderr`: diskless QEMU EGL initialization.
- `kernel-probe.serial.log`, `kernel-probe.stderr.log`: actual guest kernel negotiation.
- Probe source: `next-experiment/gpu-kernel-probe.c`.

## Next bounded validation

Build VirGL EGL/GLES against the OHOS API20 sysroot, not Ubuntu's glibc libraries. First require a genuine guest GL context, a hardware-backed renderer identification, and pixel readback. Then integrate with RenderService and verify actual desktop frames at 1920×1080. Keep the original images read-only, use only independent userdata, and delete stopped experimental userdata after preserving results as requested.

The physical display remains off. Do not disable watchdogs, skip rendering, fabricate activation/readiness, or modify account/trust/signature databases.
