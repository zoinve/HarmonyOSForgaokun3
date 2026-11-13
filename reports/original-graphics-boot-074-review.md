# Original graphics graph 074: real ashmem, composer connection and hotplug

## Independently verified progress

`reports/original-graphics-boot-074-independent.json` verifies the actual original
service graph, not a substitute client or private queue test:

- The matching real ashmem module loaded inside the guarded virtual guest with
  return zero. The kernel registered character device `10:263`, mode `0666`.
- Original RenderService's sampled backend device and composer remote pointers
  were nonzero at all three observations. The reads succeeded at their requested
  widths; guards alone are not being used to infer a successful connection.
- The original composer host (UID3036, original SELinux domain) entered the real
  reference initializer, opened DRM and completed initialization. Its unchanged
  hotplug callback was actually called and returned.
- Genuine calls subsequently entered capability/mode queries, layer creation,
  buffer submission, preparation, client-buffer handling, Commit and release-fence
  handling. **An entry trace does not establish successful return or visible pixels.**
- Original RenderService UIDs/domains, real EGL contexts and successful
  `eglMakeCurrent` remained verified. Allocator identity also remained original.

This narrows the earlier null-client failure: the original client may obtain a
remote service and still return null when SMQ initialization fails. Treating a
null stored pointer as proof of discovery failure was too strong. After supplying
the reference's omitted ashmem prerequisite, the real connection and hotplug path
now work in this virtual experiment. No service binary, identity, authorization
result, queue or callback was fabricated.

## Remaining boundaries

Original RS now addresses screen0 for backlight, but an original composer-proxy
backlight IPC failure is still logged; its cause is not established. MemMgr
service availability and failed original hidumper queries also remain unresolved.
Neither full desktop readiness nor successful composition/scanout is inferred.

This is software Mesa and a virtual VirtIO display. It is not native GPU evidence
or physical MateBook scanout. Within the bounded observation there was no
Foundation critical fault or guest reboot; that is not an unrestricted stability
claim. SELinux remained permissive with original policy and real audit records.

## Preservation and next evidence

Independent checks cover all 12 provider files, packaged ashmem module, archive,
kernel, three complete original SDK images and 378 earlier native raw files.
Ubuntu was neither connected to nor changed in this step. Failed module builds
and the generated-build-support side effect are documented in the 073 review.

075 reuses the identical verified guest archive and adds only a private QMP
observation socket. Scheduled `screendump` captures will preserve actual virtual
framebuffer pixels as PPM and lossless PNG. QMP is restricted to capability
negotiation, status queries and capture, not guest reset or input injection.
Captures and visual interpretation are pending; no desktop result is claimed.
