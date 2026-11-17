# Commercial Native 082 Design

081 proved original firmware initialization and a real wlan0/phy0 in the outer
network namespace. 082 moves that PHY once using Ubuntu's original iw 6.17 and
retains the target CLONE_NEWNET boundary and kernel capability admission.

The tool, loader, libc and two libnl libraries are SHA256-pinned read-only copies
from Ubuntu boot 33df4914-8ad8-420e-a19c-8497c4edb475. They live exclusively under
/network082 and do not replace HarmonyOS libraries. The original bootstrap and
services remain unchanged. No credentials are read, no association is requested,
and no OOBE lifecycle or activation state is changed.

After clone returns a target PID, an eight-second bounded original iw invocation
moves phy0 into that PID's network namespace. Only after exit zero does a separate
eight-second bounded helper open the target namespace, require it differs from
its own, call setns(CLONE_NEWNET), verify the resulting namespace identity and
exec original iw dev. Both command statuses and tool output are preserved. A
successful migration alone is not proof the original NetManager sees networking.

Success for this experiment requires original iw reporting a wireless interface
inside the exact target namespace. Actual association, address, routes, DNS,
NetManager integration, OOBE and genuine desktop interaction remain outstanding.
Failure does not trigger retries or removal of namespace/security checks.

The existing bounded automatic Ubuntu return and 32 MiB ESP headroom guard remain.
Archive old experimental entry contents/hashes before retaining only 081/082 entry
files; preserve all shared chain payloads and original manual/default entries.
