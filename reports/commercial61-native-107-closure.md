# Event-Triggered Two-Service Observation 107 Closure

## Operational Result

One build, installation, boot and read-only noload retrieval completed. Do not
rerun 107 or overwrite its evidence. The native interactive desktop goal remains
incomplete. The supplied original image was retained without replacement.

Run: commercial61-native-087-7e5dfa46-f6c8-405b-87a6-e04293116f4d.
Boot request: 2026-11-15 16:16:44.108789 UTC. Ubuntu return observed:
2026-11-15 16:20:28.926519 UTC (2026-11-16 local Asia/Shanghai).
Returned Ubuntu boot ID: 90d251a4-5c4d-4e5d-98e0-865f2e9f70f5.
All 133 retrieved files matched remote hashes; retrieval unmounted normally.
Final phase records target_timeout=1 and target PID 435 status 9.

The observer was the only target behavior delta. The original DFX probe and
bootstrap runtime were byte-identical to 105. Note a builder path detail: the
outer executable still loads the hash-verified runtime from the 105 directory,
not the installed identical 107 copy. This does not change the executed bytes,
but any future changed runtime must explicitly update that actual path and both
hash checks. Admission did not separately assert this candidate-path detail.

## Actual Query Overlap

Unlike 104/105, both native snapshots overlap the actual initial query and
server request. The original query event was uniquely matched to the preserved
HiLog, with SceneBoard PID 4793 and CollaborationFwk PID 957, request TID 1118.

- Query: 00:18:17.949 to 00:18:32.290 on 2026-11-16 local, 14341 ms.
- Server read: 00:18:17.950; stage 1: 00:18:29.861; reply: 00:18:32.286.
- Request to stage 1: 11911 ms; stage 1 to reply: 2425 ms.
- DeviceManager PID 749 snapshot: 00:18:18.092, 22 threads / 224 frames.
- CollaborationFwk snapshot: 00:18:18.236, 80 threads / 899 frames.
- Both native DFX calls returned 0 / Reason:success and observer status 0.

Dedicated log SHA256:
eee3307f362c7d986cf4a6dc578d18439a1a46197f5f65d4833b0b48b9a9c91c.
HiLog SHA256:
2166c39e69071aac78774195d9289de883c6cb3304d7c55e445493b20bed68f5.
See server-event-analysis.json for hashed inputs, timestamps and complete stacks.
The observer can perturb scheduling; overlap is not proof it caused no delay.

## New Blocking Evidence

The actual server request TID 1118 waits in mutex::lock under SDK SendRequest,
GetLocalDeviceInfo, UpdateLocalDeviceInfoInLock and the trusted-device request.
Collaboration initialization TID 1525 waits for Binder completion beneath
InitDeviceManager and InitPackageName.

DeviceManager has five threads waiting for the memory client's mutex beneath
SetCritical and RegisterDeviceManagerListener. TID 3391 instead waits in usleep
under SystemAbilityManagerProxy::GetSystemAbilityWrapper and GetMemMgrService.
Original logs repeatedly report missing memory service SA 1909. A source-image
libmemmgrclient disassembly in original-memmgr-audit-108 confirms the exact call
passes 1909 at 0x122fc, calls at 0x12300, and holds its mutex until 0x124c4.

sdk-lock-audit additionally verifies the SDK binary against a read-only source
image read and preserves bounded disassembly: Init's lock at 0x780d8 spans its
IPC call at 0x782e0 until unlock at 0x784a0. SendRequest locks object+8 at
0x78f30. Actual runtime mutex owner addresses and cross-process Binder transaction
IDs were not captured; do not claim a fully reconstructed ownership graph.
service-wait-summary.json preserves the compact observed dependency chain.

## Original Memory-Service Startup Lead

The image already contains memmgrservice.cfg and a run-on-create SA 1909 profile.
Its launch chain first invokes l410_memmgr_nohyperhold_ns_exec_v1, then the
original tokenized launcher and sa_main. The first wrapper's main unconditionally
binds /data/local/tmp/memmgr-nohyperhold-v1/memcg onto /dev/memcg in a private
mount namespace and exits on failure. It does not create either directory.
107's preserved phase snapshot records this wrapper as a zombie (global PID 826,
namespace PID 371). Its exact failure errno is not captured. A missing mount
prerequisite is a concrete hypothesis, not yet a proven runtime failure cause.
Read-only extracted configs, wrapper hashes and library evidence are preserved
in reports/original-memmgr-audit-108; no original binary was modified.

## Desktop And Preservation

The original watchdog reports THREAD_BLOCK_3S/6S and kills SceneBoard 4793 for
THREAD_BLOCK_6S at 00:18:32.723. Later samples retain replacement SceneBoard
9921, guide 10322 and focused guide window 8. Original OOBE recovery remains;
no setup state, certificate or activation result was fabricated. Restoring the
memory service is not established as sufficient to bypass OOBE.

Complete source frames at 120.029374 and 140.029707 seconds are 2560x1600;
rotated outputs are 1600x2560 and pixel-exact rotations. Frames differ by 6134
pixels. OCR (chi_sim+eng, psm 11) yields the Chinese welcome label and then
an unreliable two-letter fragment. The viewer rejects image inputs in this
environment; no visual inspection is claimed. Event6 keyboard delivery to
SceneBoard 9921 is verified; correlated visible desktop interaction is not.

Ubuntu remains current/default, firmware and all four original image hashes
match, screen-off timer is enabled/active, and the manual entry remains. Entry
104 was archived outside ESP before removal at 20261115T161634053021Z. Entries
105/107 remain; shared payloads were retained. 159 prior EFI files match, with
only authorized entry removal and the normal boot-managed random seed accounted
for. Exact WPA credential scanning passed 133 files / 403180296 bytes with no
credential export. All required exec sessions completed.

Seven observer tests, four overlap tests and three isolation guards passed.
These validate observation and admission only, not desktop completion.

## Next Boundary

Inspect and log the original memory-wrapper mount prerequisites before original
init. A new candidate may create only missing runtime directory scaffolding
required by the existing supplied wrapper, in the disposable RAM-backed data
filesystem. Do not invent memory metrics, alter the wrapper/token checks, remove
watchdogs or write setup completion. Verify genuine SA 1909 publication, actual
query latency, SceneBoard stability, full-resolution pixels and interaction.
Explicitly correct the external runtime path/hash checks before any changed
bootstrap is admitted. Do not replay 107 or replace the supplied image.
