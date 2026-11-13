# Settings and Xiaoyi input method: shared window-routing failure

## Confirmed evidence

Recovered the continuous logs from `native-interactive-030-f621f7c4-25e6-4e14-a568-dbf38f811ce7`, through approximately 189 seconds. These are not the older 75-second snapshots alone.

| Application/session | Input socket registered PID | Window routing PID | Outcome |
| --- | ---: | ---: | --- |
| Settings, session 74 | 2751 | 3120 | MMI cannot find PID 3120, reports a window-state error; SceneBoard closes the ability at 78.477 s |
| Settings, session 75 | 3408 | 3791 | Same routing failure, closure at 103.151 s |
| Settings, session 77 | 3655 | 4049 | Same routing failure, closure at 170.535 s |
| `com.huawei.hmos.inputmethod/MainAbility`, session 94 | 4257 | 4680 | Same routing failure, closure at 181.434 s |

The retained outer `/proc` status proves Settings is **one actual process** with `NSpid: 3120 2751`, not two applications. The window side uses its outer PID while MMI registered its target-namespace PID. No fake identity or guessed PID translation is needed to establish this mismatch. The later input-method process has no independently retained outer status; its socket/routing mismatch and identical downstream error are established, but its host/inner mapping is not separately asserted.

The observed sequence is:

1. Application creates a real window and registers its input socket.
2. Input dispatch addresses a different PID and logs `Not found pid`.
3. MMI reports the window exception.
4. `NotifyWindowStateErrorFromMMI` reaches SceneBoard.
5. SceneBoard requests `CloseUIAbilityBySCB`; the application receives background/destroy lifecycle callbacks.

This establishes the shared failure boundary, rather than attributing both disappearances to unrelated application segmentation faults or the former automatic reboot timer. Unrelated touch-pointer warnings are not sufficient on their own to explain this chain.

## Kernel boundary identified, not yet repaired

Read-only inspection of the matching native kernel source at `baremetal-identity-profile-003/linux/drivers/android/binder.c` shows that ordinary Binder `sender_pid` is translated with `task_tgid_nr_ns(sender, task_active_pid_ns(current))`, while the adaptation's extended `BINDER_GET_SENDER_INFO` reports `thread->sender_pid_nr`, assigned from `t->from_pid`/`proc->pid` without equivalent translation.

This is a concrete candidate origin for the physical-PID leak. Its call path/ABI semantics, asynchronous transactions and PID lifetime handling must be checked before changing it. Blindly replacing it with ordinary `sender_pid` would be unsafe because asynchronous Binder transactions may have ordinary sender PID zero. Do not remove PID namespaces, invent process identities, disable MMI error detection or suppress SceneBoard closure as a substitute for repairing the boundary.

No kernel change or repaired candidate was installed during this investigation. Successful Settings/input-method operation after a fix remains unverified.

## Evidence recovery and limitations

The original LAB partition required journal recovery and has historical ext4 errors. Its `ro,noload` view hid newly committed file metadata. Recovery was performed **only on a new sparse image**, never by running fsck or journal replay on the original partition.

The sparse image initially lacked newly allocated data blocks; its zero-filled file dumps are preserved but superseded. Replayed clone metadata supplied the real leaf extents; their data was read directly from the unchanged, read-only original device. Authoritative files are under `harmony-settings-inputmethod-030/extent-recovered/`:

- `interactive-hilog030.log`: 33,150,759 bytes, SHA256 `6fd7f5bdc0f8752cb707e76eca115ab46058e8f97e1bf147206d38a1ca6f9ac1`.
- `interactive-faults030.log`: 7,780,190 bytes, SHA256 `4a870d703b841f1eb2db4e72131a1100ef68313e62b85165311d1debd4c5d2b9`.
- `manifest.json`: extents, per-extent hashes and recovery method.

Both complete-file hashes were freshly verified. `shared-failure-analysis.json` and `verified-shared-failure-evidence.txt` record the assertions and raw-line excerpts.

The fault exports contain seven distinct complete JS crash reports from **Huawei Cast commonUI**, reporting an undefined `ReasonCode` in `DialogInfoUtils.ts`; these are separate faults, not replacements for the requested two applications. Input-method MainAbility is also distinct from the HarmonyKey popup that legitimately exits on outside clicks/focus loss.

No original images, target security policy, Ubuntu configuration, boot selection or original-partition metadata was changed. No new target boot was performed. The approximately 10 GiB allocated recovery image and failed recovery artifacts remain available; they have not been silently deleted.
