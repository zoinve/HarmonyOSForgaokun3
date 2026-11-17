# Settings Continuation, 2026-11-17

The user explicitly said to stop further validation and proceed directly.
Honor this priority: do not resume filesystem diff reconstruction, full disk
hashes, directory-tree checks, historical admission suites or USB experiments.

245 trialed outer journal replay using a607645696-byte metadata QCOW backup.
246 replayed only the real LAB journal, with an external undo file. Full outer
readonly fsck returned0, active165 and candidate197 file hashes were unchanged,
and their protected inode metadata/block mappings were unchanged.

247 recovered phase207 and a longer hilog, preserving both privacy scanners.
Evidence is in commercial61-native-235/runtime-evidence-recovered-247.
Two exact members are hardlinked to prior evidence; no raw tar was saved.
The recovered phase still has no final target-exit or flush markers.

248 made a64356352-byte inner metadata backup and trialed candidate journal
replay. Trial readonly fsck returned0; all six SettingsData directory metadata
records matched. It fingerprinted19487 actual visible nodes before recovery.

249 replayed the real candidate journal. Its saved private inner readonly check
returned0, but the subsequent full visible-tree fingerprint equality failed.
249 exited with failure and unmounted LAB in finally. No success result exists.
The exact tree differences have NOT been determined. Do not claim file-tree
preservation, post249 full storage acceptance, or original-service graceful
shutdown. The user directed the next step before additional investigations.
No extra8GiB data clone or device-mapper reconstruction was created.

253 keeps desktop173's original runtime binary/source and all authentication,
sandbox, provider, watchdog and hardware integration logic. Only outer init
and its wrapper digest changed. Both diagnostic loops now admit work against
the monotonic boot clock, a720s work deadline and180s reserve before900s
fallback. This prevents loop-iteration counts from being treated as real elapsed
seconds; blocking kernel I/O can still exceed software deadlines.

253 compiled and deployed through settings-workflow-254.py. No historical
admission suite was rerun. The new installer uses necessary device UUID,
Ubuntu/default/timer, RAM, transfer integrity and exclusive-file guards, but
does not run full-image hashes, fsck or directory fingerprints. It preserves
desktop173 and archives/removes only the old235 entry, retaining shared payloads.
Ubuntu's persistent default was not changed.

253 was booted ONCE. boot-attempt.json and boot-command.json are authoritative.
Do not boot again on observer timeout. There is no pending local boot-wait job.
255 completed: pinned SSH authenticated192.168.10.116, hilog grew, forced
read-only protocol worked, arbitrary shell was refused. No Settings launch
event was seen in that initial short window, and Settings window remains
unverified. The user has been asked to click Settings on the desktop.

Next work is actual Settings interaction/log observation, then collect this
same boot's terminal evidence when Ubuntu returns. Never infer UI success from
provider initialization or icon-cache MainAbility-name references. All existing
backup/undo artifacts remain private; trial raw metadata images can be removed
later after confirming they are not in use, retaining compact rollback evidence.
