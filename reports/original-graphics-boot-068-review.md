# Original graph 068 — authentic HDF queries

The isolated guest reached its 360-second observation bound. All 48 observed
SELinux samples were permissive. Original RenderService PIDs655/1162, composer
PID1173 and allocator PID1169 retained their original UIDs and SELinux domains.
Real RenderService calls created EGL contexts and successfully made them current.
No Foundation critical fault or guest reboot was observed within the bound.
This is not evidence of screen or desktop readiness.

All six bounded original HiLog queries for composer and HDF-manager exited0.
The decoded HDF output is from manager PID136 and concerns missing `hmi_service`
and `ril_ext`; it does not establish why graphics hotplug has not yielded a
RenderService screen. No useful decoded composer line was captured. Unknown
dictionary messages and console interleaving remain in the raw evidence.
Both original hidumper screen queries again exited3.

`original-graphics-boot-068-independent.json` verifies the serial, all 12 injected
libraries, initrd, kernel, three complete read-only SDK images and all 378 earlier
native raw files. Actual composer and allocator VDI mappings were observed.
No host SSH, Ubuntu setting, physical display, identity or policy change occurred.

## Next bounded diagnostic

Provider003 failed compilation because trace insertion interrupted the original
multiline LAYER_SETTER macro. Its failed build/logs are preserved. Provider004
leaves that macro unchanged and compiled successfully. The reference source is
unchanged; removal of the trace exactly reconstructs it. Original calls, returns
and the actual hotplug callback remain intact. Logging is per-process, bounded,
owner-checked, no-follow and preserves errno.

Trial069 uses provider004 plus otherwise unchanged graphics libraries, original
services and virtual-display configuration. Its observer also captures the
composer trace files. Outcome is pending; a callback is never fabricated.
