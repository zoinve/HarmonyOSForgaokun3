# Commercial 044 closure and next corrective boundary

The only boot ran 2026-11-14 19:57:20 through 20:01:02 Asia/Shanghai and
returned to Ubuntu boot 3a7be2e2-8bd5-425e-ae39-3c80ade1487e. All 63 files
match remote hashes. The configured target timeout was recorded. Seven actual
scanout exports are black. Desktop and interaction acceptance remain false.

The new observer captured 122 original ioctl records, including SceneBoard
PID 3626 UID 20020023 code 17 registration and nine sampled code 0 submissions.
Their successful ioctl returns consumed the full command. Outer samples map
SceneBoard global PID 4106 and inner PID 3626 to its handle 6, node 79926,
owned by original RenderService global PID 1141 / inner PID 823. All 21 targeted
Binder proc streams reached EOF without error. This proves observed kernel
acceptance and sampled endpoint ownership, not execution success. Original
RenderService still warns that PID 3626 has no registered application agent.

An exact original binary audit now identifies a concrete semantic mismatch.
The original service code-17 jump-table entry is 0x3f2080: it calls
IPCObjectStub::GetCallingPid, passes that value through RSProfiler::PatchPlainPid,
and supplies it to the virtual RegisterApplicationAgent method. The original
normal-mode profiler returns its input PID. The service also forwards
GetCallingPid to RSUnmarshalThread::RecvParcel. Original commercial BinderInvoker
sets its callerPid field directly from binder_transaction_data.sender_pid;
GetCallerPid reads that field, distinct from callerRealPid supplied by ioctl
0xc0286220. Current diagnostic kernel 031 preserves an authentic sender pid
reference for the latter extension but leaves standard oneway sender_pid zero.
Thus the observed oneway registration can be keyed under zero instead of the
actual SceneBoard PID. This is a causal candidate, not a verified desktop fix.

The next candidate may correct this temporary target-kernel transport semantic
using the existing held real sender PID and receiver PID namespace, only for
actual incoming oneway transactions under CONFIG_ACCESS_TOKENID. Do not use a
hardcoded process identity, change token/UID/SID, bypass service checks, modify
the original commercial userland, or change Ubuntu's normal kernel. Preserve
all synchronous/reply behavior, reference lifetime and historical kernel 031.

Post-return verification confirms unchanged original images, firmware,
Ubuntu current/default and original manual entry, enabled/active screen-off
timer, and unmounted evidence partition. Hash-matched authorized removal of
entry 042 is accounted for; 103 other prior EFI files remain unchanged and only
the normal random seed changed. Latest experimental entries are 043/044.
