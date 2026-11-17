# Commercial native 086 closure

Goal remains active: no stable interactive native desktop has been established.
This document closes experiment 086 evidence, not the desktop objective.

## Runtime evidence

- Run: commercial61-native-086-c216f99d-03e1-4504-9974-a0eb2b9f37b8.
- 129 retrieved artifacts matched remote sizes and hashes. Observation tests: 63 PASS.
- Genuine WPA association, native DHCP and default-network selection succeeded.
  Original curl returned HTTP 204 and HTTPS 204, exit 0, TLS verification result 0.
- The first startup-guide instance nevertheless timed out; later instances received
  network capabilities. Connectivity alone has not resolved callback timing.
- Original SceneBoard freeze report: 206797 bytes, complete EOF and errno 0,
  SHA256 d6168eef37a108735f3d2f2adc8e130e115090ccf3879c2340abc4860c5e61bd.
  Its main thread waits in native BundleMgr IPC GetLauncherAbilityInfoSync,
  called by ResidentLayoutCacheMgr.createDockAppInfo during Dock initialization.
  This does not independently establish the server-side cause or query argument.
- Later SceneBoard instance logged EVENT_SMARTDOCK_INIT_FINISHED. This is not
  proof that a visible desktop was reached.
- Original uitest layout requests failed accessibility permission checks and
  timed out with exit 124. No layout or interaction success is claimed.
- Complete source/output frames at 120s and 140s had matching capture/export
  metadata and zero rotation differences. The first is black; the second has
  nonblack welcome-like pixel statistics. No direct visual inspection occurred.

## Preservation

Retrieval and preservation verification initially overlapped. The first verifier
failed its LAB-unmounted assertion while the retriever held a read-only mount.
After retrieval ended, serial read-only verification passed without another boot.
Future retrieval and verification must run serially.

Ubuntu remains current/default, the screen-off timer enabled/active, firmware
and four original images unchanged, LAB unmounted, and manual entry retained.
Only authorized archived 084 entry removal is excepted. Entries 085/086 remain.
The secrecy audit found no private PSK in the 129 retrieved artifacts.

ESP free space was 33968128 bytes: only 413696 bytes above the 32 MiB guard.
Do not deploy another similarly sized overlay without a verified space plan.

## Follow-up source audit

Original SceneBoard supports external workspace configuration through
GetLayoutInfoFromConfig and DesktopDataLoader. The standard default workspace
candidate was absent in each of system, sys_prod, chip_prod and vendor images.
The separate PC-mode workspace candidate is audited by
next-experiment/audit-commercial-workspace-paths-086.py.

SmartDockLayoutConfig.getDockLayoutInfo only assigns mDockLayoutInfo when the
converted layout is nonempty (bytecode offsets 262-301); otherwise its existing
default survives. PcSmartDockLayoutConfig initializes that field from an imported
default value. Therefore an empty external layout is not an established fix.
Import resolution, valid nonempty schema and genuinely installed app identities
must be established before proposing a board-config change. Signed HAP/ABC,
provisioning state, permissions and bundle metadata remain unmodified.
