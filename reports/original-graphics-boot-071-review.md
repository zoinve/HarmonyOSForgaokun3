# Original graphics graph 071 — read-only state witnesses

## Result

- The unchanged original graph ran for the bounded 360-second VM observation.
  Independent verification recorded 48 consecutive SELinux permissive samples,
  actual original RenderService EGL contexts and successful `eglMakeCurrent`
  for PIDs 689 and 1166. No Foundation critical fault or guest reboot was
  observed within this interval. This is not desktop or screen readiness.
- In original RenderService PID1166, samples 17, 29 and 41 each successfully
  read the original HdiBackend construction guard as 1, its device pointer as
  zero, the original libcomposer device construction guard as 1 and its composer
  remote pointer as zero. All reads returned exactly their requested width,
  with errno0. Failed reads are explicitly distinguished from null values.
- Original composer PID1173, UID3036, emitted `library_loaded` only. No API
  entry, initialization or returned hotplug callback was captured.

These are private, hash-specific state observations, not an HDI ABI or a direct
execution trace. They establish that these singleton objects were constructed
and a composer remote had not been retained at the sampled instants. They do
not establish which remote-discovery branch failed, nor that a retry loop was
actually executing. State reads targeted the observer's selected (maximum)
RenderService PID, not every possible render-process role.

## Evidence and preservation

- `reports/original-graphics-boot-071-independent.json`
- `reports/baremetal-sdk-original-init-qemu-071/result.json`
- Serial SHA256:
  `82297a941a73ad0ee8c3b97ee35706f6c81ae7dd00368ba8ef3751845fc9ba85`.
- All 12 injected provider files, archive, virtual kernel, three full original
  SDK images and all 378 previous native raw files were independently checked.
- Only guest `/proc/PID/maps` and `/proc/PID/mem` were read; no ptrace, target
  writes, injected calls, identity changes, policy changes or permission bypass
  was used. Original credentials and SELinux policy remain in effect, permissive.
- No MateBook SSH operation, Ubuntu boot change or physical display operation.

## Original discovery call path

Read-only audit `reports/original-hdi-discovery-001/result.json` extracted the
genuine `/system/lib64/chipset-sdk-sp/libhdi.z.so`, without executing it or
changing the system image. Its `IServiceManager::Get()` at VA0x10610 obtains
SAMGR and requests genuine SA5100. `ServiceManagerProxy::GetService` at VA0x10e4c
writes the genuine interface token and service name, sends request code3 with
the original MessageOption flags, and returns the received remote object only
on successful IPC. Both manager lookup and named-service lookup can fail;
071 does not yet identify which failed. No fabricated reply or alternate
privileged caller was substituted.

The original `/system/bin/render_service` audit also confirms that its main
checks `RSRenderService::Init()` before entering `Run()`. Absence of a captured
composer callback must not be explained by assuming main ignores init failure.

Next: distinguish the original SA5100 lookup, named composer lookup and actual
render-process roles. Keep the working software Mesa/EGL path unchanged.
