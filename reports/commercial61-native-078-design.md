# Native 078: wait for the live desktop's original Dock completion

077 proves a transient original aa guide stop, followed by SceneBoard restart
and guide relaunch. Offline strict snapshot recovery now preserves two distinct
complete original appfreeze reports (488297 and 477045 bytes); both main stacks
wait in GetLauncherAbilityInfoSync from ResidentLayoutCacheMgr.createDockAppInfo.
The matching original BMS log at 55.716 seconds reports missing AppGallery.
This repeats the earlier 065 diagnosis; original invalid-package audit 066 is
still applicable and its authentication failures must not be concealed.

077's third SceneBoard PID 10732 genuinely completes Dock initialization at
111.025 seconds, after logging failed AppGallery and Settings queries. Therefore
078 tests startup sequencing, not a claimed BMS implementation or package fix:
keep the original SceneBoard and wait for its own EVENT_SMARTDOCK_INIT_FINISHED
log before using HarmonyMac's original aa force-stop command. Do not modify
provisioning state, installed bundles, HAP bytes, watchdog or original services.

The diagnostic reads original HiLog nonblockingly (-x), by PID (-P), with the
completion marker regex (-e). After a matching record it waits two seconds and
confirms the same PID is still present. No marker, failed read, changed PID or
uptime at least 128 seconds cannot authorize guide stop. Polls are bounded at
120; the existing outer boot/target return deadlines remain unchanged.

Seven shell scenarios pass: ready, missing services, missing marker, HiLog
failure, changed PID, expired deadline, and failed stop with exit status zero.
Archive admission proves only init, native-target/commercial-desktop077.sh and
native-target/samgr_standard005.cfg changed. The internal script path stays 077;
the distinct diagnostic service is matebook_desktop078. All original services,
bootstrap, graphics, resources and permission checks stay byte-identical.

Overlay SHA256:
7843e4c3d2ac800c19c6e6114f20a6434d548847e4f10b8d6ba2adfa1564745c.
The chain retains 001/017/016/072/073/074/075/076/077/078 shared payloads.
Only 077/078 experimental entry files remain; Ubuntu and manual entry preserved.

Success remains unproven until recovered command, lifecycle, full-resolution
pixels and genuine input response agree. A real readiness log or successful
guide stop alone does not establish desktop success or commercial activation.
