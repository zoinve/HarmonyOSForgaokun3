# User-reproduced application exits in interactive 029

## Evidence retrieved

Run `native-interactive-029-ac7f76fc-3a49-489e-89cf-360a5cd6f55c` contains 56 retained snapshots. All were scanned remotely for fault-export records and native crash signals; the SHA256 index and byte-exact final snapshot are saved in `harmony-app-exits-029/`. Its local final SHA was checked against the remote index. Current SSH access is to Ubuntu, boot ID `807db176-e0c7-402e-b417-16ca786f32e0`, not a live target session. No reproduction boot or target modification was performed.

## Confirmed Settings exit sequence

Original Settings process 2720 genuinely creates its main window and enters the foreground:

| Target log time | Event |
|---|---|
| 08:01:03.014 | `MainAbility onWindowStageCreate` |
| 08:01:03.018 | `MainAbility onForeground` |
| 08:01:10.783 | SceneBoard 2280 calls `CloseUIAbilityBySCB persistentId: 72` |
| 08:01:10.784 | Foundation invokes `CloseUIAbility` for Settings MainAbility |
| 08:01:10.786 | Settings receives `onBackground` |
| 08:01:10.847–10.848 | Window stage and ability receive destroy callbacks |
| 08:01:11.369–11.373 | Exit-reason lookup and subsequent scheduler IPC fail after teardown |

This is a foreground-to-close interval of 7.765 seconds. It establishes an explicit desktop-requested window teardown, not the previous diagnostic `aa` permission rejection. **The reason SceneBoard issued the close is not yet established.** It may not be generalized to every reported app exit, and the later IPC error must not be mistaken for an already-proven initiating cause.

No SIGABRT/SIGSEGV exit was found in the retained snapshots. Fault exports at samples 2, 5, 8 and 11 were empty. Missing optional libraries and graphics cache diagnostics also appear, but no causal link to the desktop close has been established. Do not patch libraries, input transforms, permissions, or lifecycle checks based only on these messages.

## Important collection gap

029 correctly has no diagnostic automatic restart and logs `NATIVE_INTERACTIVE029_RUNNING`. However, its passive observer and persisted parent snapshots still stop after approximately 75 seconds. Its `/data` is RAM-backed. Thus this capture does **not** cover the whole manual session, and later app faults were not automatically saved across return to Ubuntu. Empty early fault exports do not contradict the user's later reproduction.

The prior 027 automatic-test shutdown explanation is not an explanation for the reported 029 application exits. No fix or all-app root cause is claimed here.

## Next investigation boundary

Extend interactive evidence collection, without adding an automatic reboot or synthetic input: persist bounded continuous original hilog plus original fault reports, and record SceneBoard window-close reasons and corresponding real input/lifecycle events. Correlate at least two foreground application exits before selecting a shared-root-cause fix. Keep the existing 029 binary, snapshots and original SDK images unchanged.
