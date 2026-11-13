# Original service graph: vendor registration and virtual kernel

## 048: registration correction verified, not graphics readiness

The volatile init.cfg import of the **original** vendor hdf_devhost.cfg fixed the
previous missing-service registration. The independent verifier checked actual
process snapshots, not just service-start messages:

- composer_host: UID3036, u:r:composer_host:s0, PIDs810/921/1030.
- allocator_host: UID3041, u:r:allocator_host:s0, PIDs631/809/919/1027.
- render_service: UID1003, u:r:render_service:s0, several restarting PIDs.
- All 19 recorded SELinux samples were permissive. Original policy and original
  service credentials were retained; no root/sandbox substitution was used.

The original Foundation critical-process failure occurred and the guest rebooted
at ~124.87 seconds. This is **not** a stable graphics stack or desktop result.
The critical/watchdog protections were not disabled. A composer readiness
parameter write was denied by the original parameter service; no fabricated
readiness or parameter-permission bypass was introduced.

Evidence: reports/original-graphics-boot-048-independent.json and
reports/baremetal-sdk-original-init-qemu-048. Serial SHA256:
817d0a743ee2f5817c8c70b482442547f17016515328bf667daa09e4da5b10e8.
The verifier rehashed all 378 earlier native logs and all three original images.

## 049: virtual graphics kernel baseline

A fresh guest used isolated kernel002 (SHA256
a75433f6f069d6607d3a34c461ae3723287d7ae67d45d72a68c7983f12a50136)
and QEMU virtio-gpu-device. The initrd was exactly the completed048 package;
no replacement VDI was applied in this baseline. Original composer/allocator
processes and the original vendor VDI mappings were observed, but Foundation
again reported a critical fault. The 160-second observation timed out, with
24 permissive samples. No virtual DRM initialization was evidenced by the log;
attaching a device is not proof of a bound kernel driver or usable scanout.

The serial hash was independently checked against result.json:
2434f7725f308ae866100fe034f98967793b333fb437589c947b76559b3d6011.
The runner recorded all original images, native config and critical sources
unchanged. No physical MateBook boot or SSH operation occurred in this phase.

## Integration now in progress

Reference HarmonyMac composer and buffer VDIs were compiled against the platform
std::__h ABI and the hash-pinned genuine SDK 56-byte BufferHandle library.
No stale private SDK libraries are copied into the original root. Provider002
contains only the two replacement VDIs and OHOS-musl libdrm. Mandatory composer
exports and DT_NEEDED libraries were checked; original references/images were
rehash-verified unchanged. Provider001 failed because a cpio symlink was mistaken
for ELF data; its outputs remain intact and provider002 resolves the pinned
symlink target explicitly. Neither build executes a target ELF.

Candidate050 uses a RAM-only vendor overlay, original init/HDF configuration and
credentials, and real sysfs-backed virtual DRM nodes. Missing DRM must fail rather
than create fake devices. This is virtual-service integration, not physical
scanout; EGL/Mesa replacement and desktop readiness remain subsequent work.

### 050 safety gate result

Candidate050 ran once and refused before executing original init. Actual sysfs
enumeration reports virtio0 device0x0010 with driver=UNBOUND; all four block
devices bind virtio_blk. No DRM nodes were present, so the fixture did not create
fake character devices or apply the provider overlay. The early HANDOFF marker
is an *attempt* marker printed before this guard, not proof of original-init exec.
Guest powered off normally after the refusal; QEMU rc0 is not experiment success.
Serial SHA256: 910fc1395030667c4c2c41a61c38191795b8cfcaa25e298a565af5a41f228f7c.
All image/kernel/native/source preservation checks passed. Candidate051 adds only
kernel initcall tracing, reusing the exact050 fixture, to identify the unbound
driver cause. Completed050 is not rerun or relabelled successful.

Provider002 C++ compilation retains reference-header unused-parameter and any
reference-source format warnings in compile-*.stderr; this is not a warning-free
build claim. C DRM source uses -Werror; no reference source was edited.
