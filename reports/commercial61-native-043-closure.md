# Commercial 043 closure

The unique boot ran at 2026-11-14 19:40:43 through 19:44:24 Asia/Shanghai.
Ubuntu returned with boot ID 662eaa0e-54d6-44d9-87c1-9de861a84d31.
All 63 recovered files match remote hashes. The target timeout was recorded.
All seven scanout captures remain black; desktop and interaction are unverified.

The ioctl hook demonstrably executes: 74 records form 37 successful, consumed
outgoing command pairs. SceneBoard PID 3542, UID 20020022 has a RenderService
descriptor request on handle 5 and connection descriptor requests on handle 6.
No commit-delivery conclusion follows from the missing code 0/17 records:
the exact original CommitTransaction FillParcelWithTransactionData starts with
an int32 zero and transaction version, not an interface token. The original
RegisterApplicationAgent starts with WriteRemoteObject, likewise without a
token. The descriptor filter cannot recognize either parcel. Historical 042
and the 043 candidate statement are preserved, not rewritten as successful
transaction-delivery evidence.

All three process maps reached EOF without error: RenderService 121764 bytes,
SceneBoard 562555 bytes, its observed secondary process 364683 bytes. Mapping
paths do not by themselves prove a duplicated-runtime fault. Binder global
transaction rings were read successfully. Individual Binder proc paths failed
with ENOENT because the original kernel names them using current->tgid in the
outer namespace, not the inner procfs PID. This is an observation defect, not
evidence of a missing Binder process.

Post-return verification confirms the four unchanged original images, unchanged
firmware and Ubuntu current/default, original manual entry, unmounted evidence
partition, and enabled/active screen-off timer. The hash-matched authorized
removal of entry 041 is accounted for; 102 other prior EFI files are unchanged,
with only the normal random seed changing. Entries 042/043 are retained.

The next bounded candidate must associate tokenless code 0/17 with a previously
observed exact connection descriptor on the same process/fd/handle, explicitly
label this association, and correlate real kernel endpoints from the outer
PID namespace. It must not modify requests, identities, registration, token
checks, service startup, or desktop content. Kernel acceptance remains distinct
from server execution and final pixels.
