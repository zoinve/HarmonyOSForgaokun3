# Commercial native 050 candidate

Observe real original RenderService execution on exact kernel 045, which
previously completed the bounded target run. Do not reuse trace kernel 047
or its 1216-byte modules. The full 050 archive must differ from full 045 only
in outer init; all modules, original bootstrap and original userland remain
byte-identical. Preserve authentic oneway caller PID handling and all original
service credentials, authentication, token and sandbox checks.

Use target-thread perf hardware execute breakpoints at four audited original
ELF entry offsets: request, register_agent, recv_parcel and on_vsync. Resolve
actual executable maps by inode/device and compare original entry bytes.
Match the original child PID namespace before attaching. Do not replace user
instructions, mount tracefs, write perf sysctls or dereference target objects.

Sample x0 through x6 only, with monotonic time, IP and actual perf PID/TID.
Use bounded rings/slots and log attachment errors, malformed/lost samples,
suppressed output and event counts. Missing samples are not nonexecution
proof. A failed observer does not fabricate success or alter original services.
Close every event before the target timeout cleanup.

Keep 150-second target and 270-second outer deadlines, authorized permissive
SELinux support/policy, original images and Ubuntu default/current, manual boot,
firmware and screen-off timer. Keep only the latest two experimental entries
after archiving removed entry contents and hashes; preserve shared payloads.
Do not repeat 045 or any completed operational experiment.

Build/tests do not prove hardware breakpoint support at runtime or a desktop.
Real native desktop pixels and interaction remain the required final outcome.
