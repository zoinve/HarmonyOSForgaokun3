# Event-Triggered Original Service Capture 107

The desktop remains incomplete. 104 captured after the query and 105 before it.
107 replaces only the observation worker. No original service, binary, package,
identity, network configuration, setup state or lifecycle recovery is changed.

The observer waits for one current SceneBoard PID, starts its own original hilog
reader, and accepts only that PID's main-thread CFWKProxy query-start log. The
reader is bounded to 90 seconds; absence, ambiguity or SceneBoard replacement
refuses capture. It then invokes the unchanged reference native DFX probe once
for DeviceManager and once for CollaborationFwk, with explicit uptime markers.
Its private FIFO and reader are cleaned up. It does not kill either service.

Hypothesis: DeviceManager listener registration blocks SDK initialization and
serializes the synchronous query. A query-triggered DeviceManager stack can
identify a deeper dependency. Capture overlap must still be proved afterward;
trigger success alone does not establish it. DFX can perturb scheduling.

OOBE's original recovery remains a distinct unresolved path. These captures
are not a proposed OOBE bypass, and fixing latency is not desktop acceptance.
The supplied image is unchanged. The reference's external accepted runtime is
not present in the local public checkout; do not infer an image mismatch.

Admission requires archive delta isolation, unchanged original probe/bootstrap,
observer failure tests, three QEMU isolation guards returning 77, full ordered
overlay equality and unchanged inherited one-boot/preservation/privacy gates.
Only after admission may 107 be installed and booted once. Archive older entry
104 outside ESP before retention cleanup; retain 105/107, Ubuntu and manual.
Full-resolution frames and correlated visible interaction remain acceptance.
