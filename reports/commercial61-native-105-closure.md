# Native server observation 105 closure

## Result

Completed one build, installation, boot and read-only noload retrieval. Do not
rerun operational experiment 105 or overwrite its evidence. A stable interactive
native desktop remains unproven. The supplied original image remains the input;
an image difference from HarmonyMac has not been established.

Run: commercial61-native-087-dabf50fa-484d-4e90-ae44-a6aea16645e6.
Boot request: 2026-11-15 15:52:07.197809 UTC. Ubuntu return observed:
2026-11-15 15:56:14.243626 UTC. Returned Ubuntu boot ID:
deb50a73-c0df-4174-a4bd-8bc1f35c20e3.
All 133 retrieved files matched remote hashes. Retrieval is unmounted.

## Capture And Initialization

The unchanged reference DFX probe captured 80 threads and 741 frames from
CollaborationFwk PID 936. Its native API returned 0 / Reason:success.
Dedicated log SHA256:
db0950cfc84e8165628a7173e4958e4195719b16d596da9ee3c111c77ee1c64a.
The observer invoked DFX before the proc survey, uptime 66.57 to 66.80.

Snapshot timestamp was 23:53:41.227 local target time. SceneBoard PID 4878's
query ran 23:53:42.302 to 23:53:48.400 (6098 ms). Server request TID 965 spent
6086 ms before stage 1 and 10 ms from stage 1 to reply. The snapshot preceded
query start by 1075 ms: it did not capture the query's blocking instruction.
See server-capture-timing.json for original log line references.

The snapshot nevertheless records real startup contention. Thread 1566 waits
in original Binder SendCmd beneath IpcClientManager::Init and
DeviceManagerImpl::InitDeviceManager. Other threads wait in the SDK mutex path
under IpcClientManager::SendRequest and GetLocalDeviceInfo.
Original initialization logs show keyMouse initialization from 23:53:36.343
to 23:53:43.569 and raiseHandAdv initialization from 23:53:43.569 to
23:53:48.381. Stage 1 follows the latter completion by 8 ms.
This supports investigation of initialization serialization, not proven query
causality or ownership of the actual mutex during the uncaptured interval.

Read-only SDK inspection shows Init and SendRequest both lock the manager's
object+8 field. IpcClientProxy Init and SendRequest both forward through their
object+8 manager pointer. These field offsets alone do not prove that the
captured calls share the same runtime manager instance or mutex.

## OOBE And Pixels

Reference aa force-stop reports success, but original SceneBoard recovery
relaunches the guide. SceneBoard PID 4878 survives later samples; guide PID
8176 and focused guide window 72 remain. No completion state was fabricated
and original lifecycle recovery was not disabled. Improving the query latency
alone has not been shown to prevent OOBE recovery.

Frames at 120.004451 and 140.004483 seconds preserve source resolution
2560x1600 and rotated output 1600x2560; rotation comparison is pixel-exact.
Frames differ by 7804 pixels. First OCR is empty; second OCR recognizes the
Chinese welcome label. No visual inspection is claimed. Pixel changes and
OCR are not desktop acceptance.

The physical event6 keyboard pair reached SceneBoard at 23:54:47.679/.745.
input-response-analysis.json confirms framework delivery, not a correlated
visible desktop interaction.

## Preservation And Privacy

post-return-verification.json confirms Ubuntu current/default, the original
manual entry retained, firmware and all four original images unchanged,
158 prior EFI files unchanged, and screen-off timer enabled/active.
Entry 101 was archived outside ESP before authorized removal; entries 104/105
are retained. The normal boot-managed random seed is accounted for.

evidence-secrecy-audit.json confirms the original private configuration hash,
no exact credential value in 133 retrieved files / 380620092 scanned bytes,
and no credential export. Native identity helper evidence does not establish
commercial activation as a prerequisite for reaching a development desktop.

## Next Decision

Do not repeat fixed guide-relative capture delays: 104 was late and 105 early.
Any new observation should be tied to an original query event or investigate
DeviceManager registration dependencies, with original checks preserved.
Keep OOBE recovery and SDK latency as separate unresolved threads. HarmonyMac's
unconditional READY and successful force-stop do not prove stable OOBE bypass;
its accepted external runtime is not available in the pinned Git reference.
The acceptance target remains full-resolution native desktop pixels and a
correlated visible interaction, not a successful probe or absent guide PID.
