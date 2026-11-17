# Native 101: Reference-Scoped SoftBus Preload Removal

Hypothesis: the supplied image retains the L410 BLE SoftBus preload which
HarmonyMac explicitly removes; preserving this platform-specific adaptation
may contribute to divergent native service behavior and desktop responsiveness.
100 correlates a 21.274-second device collaboration synchronous query with
15.747-second native-to-JavaScript OOBE exception dispatch delay. Neither the
preload's causality nor a persistent guide dismissal is established.

The sole service change is deletion of the exact LD_PRELOAD entry naming
/system/lib64/l410-collaboration/libsoftbus_ble_pc_rsp_preload_v1.so from the
original SoftBus JSON. All other service fields, jobs, credentials, permissions,
executables and security/lifecycle checks are structurally unchanged. The JSON
is installed in the existing read-only RAM system overlay before original init.
The integration bootstrap is rebuilt for that one copy operation and marker;
the outer loader points to the new pinned bootstrap, and the genuine early
hardware wrapper only updates its outer-core digest. Original images are not
modified. No account/SoftBus restart, completion-state edit or repeat kill is added.

099's reference script, startup bridge, real identity/network, bounded shutdown,
full-frame captures and physical keyboard input remain unchanged. A read-only
observer samples config digest and SoftBus preload mapping without exporting
environments or raw mapping contents. Five samples are observations, not proof
of process continuity or desktop success.

Before boot: require exact archive/source deltas, config regression tests,
isolation guards, full overlay-chain equality, strict host-key checks, genuine
image hashes, active screen-off, Ubuntu current/default, free RAM and EFI space.
Retain only 099/101 entries after hash-archiving the removed 095 entry outside
the ESP; never remove shared payloads. Install and boot 101 at most once.

After bounded Ubuntu return, retrieve the new run serially using read-only
noload mounting, verify every exported file and identity/credential privacy,
and unmount before other preservation operations. Compare actual service
mapping, query latency, WMS guide focus, full-resolution pixels and visible
input response. An empty trusted-device list or unchanged OOBE relaunch is
neither a successful fix nor an activation failure diagnosis. Preserve negative
results. Native desktop acceptance still requires stable visible interaction.
