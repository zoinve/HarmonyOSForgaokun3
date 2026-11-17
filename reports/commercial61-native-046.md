# Commercial 046 candidate: actual original service execution trace

Desktop and interaction are not verified. 045 removed the prior missing-agent
warning and showed real SCBDesktop scene nodes, but recorded zero composer
frames after the first SceneBoard ArkUI flush at 78.800 seconds. This candidate
observes the actual original service execution path, not just outgoing ioctl
consumption or ELF-symbol preload wrappers bypassed by internal binding.

Independent target kernel native-trace-kernel-046 retains the exact 045 source
and authentic namespace-aware oneway sender PID. Image SHA256 is
3c1dfeb202d88687c6a72007b4e0b904deab1078257405730a3ab02b4acf4623,
20,695,552 bytes. Config changes add tracing infrastructure only. Original
045 source/config and Ubuntu kernel are unchanged. Return-value overriding
and function/function-graph tracing are not enabled.

Fourteen original service/base methods have verified original ELF hashes,
file-backed executable segment offsets and exact entry instruction words.
Probes cover OnRemoteRequest, real agent registration PID, RecvParcel,
transaction unmarshal, cached data, commit, process, VSync and SendCommands.
Only actual argument registers and selected return registers are recorded;
there are no private-object layout reads, identity substitutions, replacement
service implementations or manufactured responses. Kernel-managed probes
are transient in target memory; original ELF files are not rewritten.

Outer setup matches the actual original render_service command and exact
child PID namespace, then validates entry instructions through its real root.
Tracing uses a bounded ring and bounded stream exports. Setup failure disables
the candidate probe group and leaves original services running. Missing or
truncated trace records cannot establish a method did not execute. Runtime
registration syntax and probe hits remain unverified until this boot.

Original inner bootstrap source and binary hashes are unchanged from 045.
Outer adds only trace collection and new evidence labels. Static protection
tests passed; full/incremental package equality passed. Increment SHA256 is
a6c1c6d54b283d3574b695729c520a5fa7a7427eeb4e2a14745b445e3349961b,
1,088,619 bytes. Original DTB031, original init/desktop launch, authentication,
token/UID and sandbox checks, loaded SELinux support with permissive target
mode, 150-second target and independent 270-second outer bounds are retained.

Installation preserves all 109 prior EFI files and leaves 166,723,584 bytes
free. Both non-PID1 guards exit 77. Ubuntu default/manual entry and enabled
screen-off timer pass. No reboot was requested by installation. Per user
retention policy, archive/remove only old entry 044 before the sole boot,
keeping experiments 045/046 plus Ubuntu/default and original manual entry.
All shared payloads and numbered historical evidence remain.

Three references remain combined: L410 original-service/namespace and board
backend boundaries, HarmonyMac native original RenderService/EGL/queue route,
and Linux Compatibility Platform application compatibility after the native
desktop path works. No standalone microtest or substitute UI is acceptance.
