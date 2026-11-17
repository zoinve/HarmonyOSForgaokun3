# Native desktop experiment 109 closure

## Execution

One build/admission/install/boot/retrieval, all terminal. Do not rerun.
Run: `commercial61-native-087-8c690eb5-863b-48c3-a0a9-6c123e8b06c2`.
Boot request: 2026-11-15T17:04:27.312974+00:00.
Ubuntu return: 2026-11-15T17:08:34.317859+00:00.
Ubuntu boot ID: `b705c9d1-99df-414f-8b3d-0bb365b218fb`.

Observation-only change over 108: fork the dedicated original memory-service
observer from the existing monitor and export its dedicated log. Outer init and
its integrity wrapper updated for export. Full ordered archive chain verified.
Actual runtime intentionally remains the byte-identical 108 runtime at its 108
path, with both original hash checks preserved. Installed admission additionally
verifies that actual remote runtime path. No original service/token/namespace
wrapper, original image or original desktop recovery changes.

Overlay SHA256:
`ab710ccea2ffa3f137514277b71f7e8fbf1505240649b2e2a99d10d97af4f33c`.
Runtime SHA256:
`81c2fb7d8a613b683c9ed6e4d278032f6dd7626af7995f263839bca791f9dda2`.

## Original memory-service evidence

Both native DFX calls genuinely succeeded against namespace PID 467:

- First: timestamp 1970-01-01 08:00:20.233, 8 threads / 55 frames.
- Later: timestamp 1970-01-01 08:00:40.467, 9 threads / 62 frames.

Those timestamps precede guest wall-clock synchronization; they are not the
calendar time of the experiment. Actual service initialization was not captured.
Main thread is in Binder StartWorkLoop/JoinThread in both snapshots. Other
threads include original IPC, watchdog, FFRT and ReclaimStrategy wait loops.
These snapshots do not distinguish an earlier Init failure from Publish failure.

Both namespace surveys show that the original wrapper genuinely bind-mounted
the disposable-data directory onto its private `/dev/memcg`:

`/local/tmp/memmgr-nohyperhold-v1/memcg /dev/memcg ... - ext4 /dev/loop3 ...`

The service sees directory mode 0755, root ownership, and `total 0` contents.
It is an empty ext4 directory, not a memory cgroup filesystem. This is a verified
interface difference, not yet a proven specific failing initialization branch.
No synthetic kernel files or memory metrics were created.

Original CheckSystemAbility finds SA1909 absent at all seven targets 20 through
140. DeviceManager and CollaborationFwk DFX snapshots both overlap the actual
desktop query/request. Query takes 19593 ms; request-to-stage1 takes 14753 ms.
Do not infer that DFX caused or fixed the timing; observation may perturb it.

## Static interpretation limits

Original OnStart checks Init before Publish, and checks Publish separately.
ReclaimStrategyManager checks SetRootMemcgPara, which calls
Memcg::SetMemcgParamToKernel at 0x1d35ec. The latter reads/writes actual kernel
parameters; absence of those interfaces needs exact return-path/log correlation.

The field at Memcg offset 56 checked at 0x1d3548 is NOT a filesystem-existence
check: Memcg's constructor allocates a ReclaimRatios object and stores it there
at 0x1cfba4. Do not misdiagnose this pointer check as missing cgroup files.
The original ELF retains an `_hilog_` dictionary section; recovering genuine
early messages is a possible next diagnostic, not yet completed.

## Desktop, pixels and preservation

Reference force-stop succeeds but original OOBE relaunch still occurs. Guide
PID 9116 owns focus window 72 at 90/110/130/145; SceneBoard PID 4863 is present.
Keyboard events reach SceneBoard; visible interaction is not proven.
120/140 frames preserve 2560x1600 pixels and exact clockwise rotation;
5210 pixels differ. Image viewer unavailable, OCR unreliable. No desktop claim.
Original bounded target exit: timeout=1, PID435, status9.

135 files matched remote hashes; read-only noload retrieval unmounted.
Credential audit: 135 files / 385354395 bytes, no network credential export.
Original images, firmware, default/current Ubuntu, manual entry and enabled/active
screen-off timer unchanged. Retention archive
`boot-entry-retention-20261115T170417726215Z` removes only 107 entry, retains
108/109 and all shared payloads. 161 prior EFI files unchanged; loader random-seed
update accounted for. Eighteen helper/observer tests and three isolation guards
passed before install. Unrelated tracked deletion of verifier067 preserved.

## Next step

Keep the real native desktop goal active. Use the newly established private
empty-memcg view to investigate original initialization errors and actual kernel
interface requirements. Do not synthesize SA1909, memory metrics, identities,
setup completion or activation, and do not suppress original failures or recovery.
An additional boot must bring a new discriminating observation or real fix.

Authoritative artifacts in `commercial61-native-109/`:
`memory-stack-analysis.json`, `memmgr-runtime-analysis.json`,
`server-event-analysis.json`, `reference-runtime-analysis.json`,
`post-return-verification.json`, `post-return-review.json`,
`input-response-analysis.json`, `evidence-secrecy-audit.json`, retrieval manifest.
