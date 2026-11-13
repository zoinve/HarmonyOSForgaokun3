# Original-service EGL diagnostics 055–056

## Actual result

Both isolated virtual-display boots reached original RenderService under its
original UID 1003/domain and SELinux permissive policy. Neither demonstrated
graphics readiness or a desktop; Foundation critical faults and guest reboots
remain. These are WSL/QEMU observations, not MateBook physical display results.

055 mapped the replacement bridge and Mesa but captured no trace files. It is
not evidence that EGL calls succeeded or were absent. Independent evidence is
`original-graphics-boot-055-independent.json`.

056 moved the diagnostic directory to the disposable `/data` filesystem and
added a reversible bridge constructor witness plus observer directory metadata.
Actual records prove the constructor ran in original RenderService PIDs
481, 805, 890, 1016 and 1132 (UID value 0x3eb), and the real Mesa library handle
was non-null. The observer confirmed directory mode 01777. This does not isolate
which of the two diagnostic changes resolved 055's missing records.

However, repeated successful Mesa symbol-resolution logging exhausted the
256-record per-process limit before useful EGL operation results were recorded.
Thus 056 is a load/visibility result, **not** a GPU initialization result.
The independently verified serial SHA-256 is
`1a5c0865e48eafd53eed1912b45b3e31bfcf300c7a66ef6bd102c5cad910665c`.

## Follow-up

Bridge package 005 logs the successful Mesa-library handle only once per
process, before the existing bounded record counter. Other real calls and
results remain delegated exactly as before; EGL error state is not consumed.
Trial 057 reuses the exact 056 bootstrap, virtual kernel, original service
configuration and private Mesa closure, changing only this diagnostic bridge.
No outcome for 057 is asserted here while it is running.

## Preservation

056 independent verification rehashed all three original SDK images, the actual
initrd and twelve injected provider files, the virtual kernel and all 378 prior
native raw files. Twenty observed mode samples were permissive. Original service
UIDs/domains were verified. No original SDK/platform libc++ replacement, identity
spoofing, service binary patch, sandbox removal, Ubuntu security/boot change or
physical GPU access occurred. Ubuntu was not contacted in this work segment.

Original RS disassembly identifies a GPU-context initialization failure path
that returns before HgmRenderContext allocation; later VSync dereferences that
null member. The actual failing EGL operation remains to be established, not
papered over by patching the original RenderService.
