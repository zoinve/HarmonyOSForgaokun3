# OHOS Freedreno build 002 and isolated native test

## Scope

Mesa 25.0.1 was cross-built for OHOS/AArch64, Freedreno/MSM, EGL/GLES and
GBM using retained sources and dependencies. Vulkan, LLVM and dependency
downloads were disabled. Configuration, compilation and DESTDIR staging
completed; all 34 staged regular files were independently checked against
their recorded byte counts and SHA-256 hashes. The legacy library prefix and
Mesa sources were unchanged by build 002. The C++ narrowing diagnostic
compatibility flag does not prove that generated GPU commands are correct.

## Isolated runtime package

`baremetal-freedreno-probe-package-001/package.json` records eight AArch64
ELF files: the probe, EGL, GLES2, GBM, Gallium, libdrm, the original SDK runtime
loader/libc, and the NDK C++ runtime. `libc.so` is a relative symlink to that
loader. All DT_NEEDED names and strong dynamic symbol references have matching
providers in the package; actual loader compatibility still requires execution.

The loader is the retained unmodified SDK extraction
`next-experiment/official-gpu-probe-924/official-loader.so`, not the NDK libc
link stub. Its SHA-256 is
`f7947b746dc4169677321b18ee77e4f4f158fde75762b2d9a3ae107b277c0181`.
The package archive is 6,351,353 bytes, SHA-256
`1c79a3f222b2b2c9492fa6ab19ed35f7b162f0efe8e6dc1c3aa23d143b7e8eb5`.

The probe selects `/dev/dri/renderD128` explicitly through EGL device
enumeration, requires renderer `FD690`, and checks a red triangle center and
blue background corner including opaque alpha. Native C policy tests reject
VirGL, software/other renderers and malformed pixel results. These policy
checks do not themselves execute the GPU.

## Runtime protections and acceptance criteria

`next-experiment/run-baremetal-freedreno-probe-001.py` stages only its private
hash-checked files, then uses a bounded transient systemd service: UID 1001,
supplementary render group, no effective capabilities, no-new-privileges,
read-only system/home isolation, private network/tmp and a closed device
policy allowing only the render node in addition to systemd's standard
pseudo-devices. A separate service with the same restrictions must demonstrate
that renderD128 opens while card0 is denied before rendering starts.

It does not replace system libraries, acquire DRM master, modeset, modify
boot entries or reboot. It uses an explicit OHOS loader/library path; there
is no need for host-wide loader configuration or relaxed file permissions.
Runtime timeout and memory limits cannot guarantee recovery from a GPU or
kernel hard lock.

Runtime results belong in `baremetal-freedreno-probe-run-001/result.json`.
Only a zero process status plus the probe's triangle/readback completion
marker establishes this limited test passing. No result establishes physical
scanout, HarmonyOS compositor integration, Binder/access-token compatibility,
or a native HarmonyOS desktop. Ubuntu's automatic screen-off timer remains
enabled; the test contains no display wake request.

## Actual native results

Run 001 completed on the running Ubuntu kernel `7.1.0-rc3-gaokun3+`, using
the OHOS runtime and the packaged OHOS Mesa libraries:

```text
FREEDRENO001_DEVICE index=0 render_node=/dev/dri/renderD128
FREEDRENO001_EGL version=1.5 vendor=Mesa Project
FREEDRENO001_GL renderer=FD690 version=OpenGL ES 3.2 Mesa 25.0.1
FREEDRENO001_PIXELS center=255,0,0,255 corner=0,0,255,255
FREEDRENO001_PASS shader_triangle_and_readback desktop_not_tested=1
```

Its sandbox admission service demonstrated UID 1001, zero effective
capabilities, no-new-privileges, render-node access and denial of card0.
An independent check subsequently verified all eight deployed ELF hashes and
sizes and observed GDM already logically off, with the screen-off timer
active. That verifier explicitly rejected display-setting commands.

**Policy-evidence correction:** querying a successful transient unit after
`systemd-run --wait` returned found a garbage-collected unit. Consequently,
run 001's `effective_service_properties` contains unloaded defaults, not the
actual running policy. A fresh query confirmed `LoadState=not-found` and
`Transient=no`; those defaults are not evidence of the executed restrictions.
Run 002 added a pre-execution policy query, but failed its sandbox admission
because `%n` was passed literally in a transient ExecStartPre property. A
separate harmless printf service reproduced the literal `%n`. No GPU probe
was executed by run 002. Its failure logs remain unchanged.

Run 003 substituted the literal unit name before passing the transient
property. Both the admission service and GPU service then captured their
**loaded, transient** policy before execution: User=zoinve,
SupplementaryGroups=render, DevicePolicy=closed, only renderD128 allowed,
CapabilityBoundingSet empty, NoNewPrivileges=yes, ProtectSystem=strict,
ProtectHome=yes, PrivateNetwork/PrivateTmp=yes, RuntimeMaxUSec=45s,
MemoryMax=536870912 and TasksMax=32. The unchanged package again produced
the exact red/blue opaque pixels above and exited zero. Neither actual GPU
run added kernel log lines during its captured interval. No reboot occurred.

Evidence:
- `baremetal-freedreno-probe-run-001/result.json`
- `baremetal-freedreno-probe-run-001/independent-verification.json`
- `baremetal-freedreno-probe-run-002/remote.stderr`
- `baremetal-freedreno-probe-run-003/result.json`

## Remaining graphics caveat and next boundary

Mesa emitted a non-fatal `os_same_file_description` warning with
`Invalid argument`, followed by its documented same-device-FD fallback.
The existing `src/util/os_file.c` uses `kcmp` when SYS_kcmp is available and
otherwise cannot establish FD identity. The exact runtime/build reason for
this warning remains unverified; no privilege, syscall policy or security
configuration was relaxed to suppress it. This matters particularly before
multi-FD DMA-BUF/GBM sharing tests and compositor integration.

This milestone proves this particular OHOS EGL/GLES offscreen draw/readback
on native hardware. It does not prove GBM allocation/import interoperability,
native-window/compositor/display-HDI integration, exhaustive GPU stability,
or HarmonyOS boot readiness. The SDK7 access-token/SPM and Binder ABI gaps
in `baremetal-harmony-abi-audit-002.md` remain unresolved; do not replace
those interfaces with success stubs merely to start a desktop.

Fresh targeted checks after the runtime work passed: native C renderer/pixel
policy harness, four screen-off policy tests and four immediate-reconnect
tests. These are scoped checks, not a claim of a unified repository suite.
Inline review checked private extraction paths, dependency isolation,
render-only restrictions, runtime limits and the distinction between GPU
evidence and desktop readiness. No subagent, commit or push was used.
