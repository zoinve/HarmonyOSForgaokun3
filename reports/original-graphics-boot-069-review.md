# Original graphics 069 — loaded provider, no observed initialization

## Verified result

`original-graphics-boot-069-independent.json` independently checked the single
completed 360-second isolated QEMU observation. All 48 SELinux samples were
permissive. Original service UID/domain checks and all preservation checks
(12 injected graphics files, initrd/kernel, three original SDK images and 378
previous native raw logs) passed. No Foundation critical fault or guest reboot
was observed within the bound; this is not desktop or graphics readiness.

Original RenderService PIDs 657 and 1161 successfully created EGL contexts and
returned true from the real `eglMakeCurrent`. Original composer PID 1164,
UID 3036, recorded only `library_loaded`. No initialization-stage or hotplug
callback-return trace was captured. This establishes library loading, not a
successful adapter connection, screen enumeration or callback. The mapped VDI
path is `/vendor/lib64/libdisplay_composer_vdi_impl.z.so`.

All six original composer/HDF-manager HiLog queries exited zero; successful
query execution alone does not establish service registration or a screen.
`actual_hotplug_callback_returned`, readiness, desktop and physical-board
verification remain false. Original callback behavior and service binaries
were not changed or replaced with success stubs.

## Next boundary

Investigate original HDI service discovery/registration and client connection
before modifying working EGL drawing code. Read-only inspection of the genuine
vendor `hdf_default.hcb` confirms the expected `composer_host`,
`libdisplay_composer_driver_1.0.z.so` and `display_composer_service` names
(HCB SHA-256 `27b26f9a105b1fb0fa80f956032fac753576e4f1d1ab1e71ac1b6f1fbc25c118`).
This rules out a simple missing-name hypothesis, not all HDF configuration issues.

Unsupported access-token permission ioctl messages remain a separate compatibility
lead, not an established cause of the screen failure. No authentication check,
parameter DAC rule, service identity or Ubuntu host setting was bypassed.

All runtime activity was inside the isolated local WSL VM. No MateBook SSH,
host reboot, physical scanout, download, commit or completed-experiment rerun
was performed in this step.
