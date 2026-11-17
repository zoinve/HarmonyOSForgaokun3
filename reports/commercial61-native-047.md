# Commercial native 047 candidate

Goal: observe original RenderService execution after real SceneBoard transactions
and obtain a native desktop, not a replacement renderer or synthetic service.

046 persisted no runtime directory. The matching trace configuration changes
module structure size from 1152 to 1216 bytes. This candidate rebuilds the
kernel, all initrd hardware modules, and unchanged adapted ashmem source
together. Module dependency closure and fresh subset indexes are required.

The original inner bootstrap is byte-identical to 046. Original services,
authentication/token checks, permissive SELinux support and policies, desktop
launch order, authentic oneway Binder PID handling, observer 044, and bounded
150-second target / 270-second outer deadlines remain. Trace events use group
commercial047. No forced module loading is used.

Full and incremental archives must be proven equivalent under the ordered
001 / 017-directory / 016-hardware / 047 chain before installation.
Keep Ubuntu current/default, original manual boot entry, image hashes,
firmware and screen-off timer. Keep the latest two experimental entries,
archiving older entry contents/hashes outside ESP before authorized removal.
Never rerun the completed 046 operational experiment.

At creation this candidate has not been booted; native pixels, interaction,
runtime probe attachment and service execution remain unverified.
