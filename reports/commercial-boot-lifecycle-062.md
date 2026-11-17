# Boot lifecycle investigation 062

## Scope

Read-only original-image/static analysis and completed run 061 evidence review.
No new operational boot, deployment, account CLI execution or boot-flag write.
Desktop remains unverified and black in 061 sparse captures.

## Original Lifecycle

Original /system/bin/bootanimation SHA256:
51e312f723a36af50907e48cbe6cd191da021fdaeca6a3d2d43b4badf1eaf84a.
Its own .gnu_debugdata identifies BootAnimationStrategy::CheckExitAnimation
at VA 0x198fc. The supported default path logs animation end, writes
bootevent.bootanimation.finished, then reads bootevent.boot.completed.
BootCompatibleDisplayStrategy::Display polls CheckExitAnimation with a 30 ms
sleep until it returns true. Animation-finished is not process-exit permission.

BootAnimationOperation destructor VA 0x16aec calls DetachToDisplay at 0x16b20,
RemoveFromTree at 0x16b30 and FlushImplicitTransaction at 0x16b34. These are
static callsites, not evidence that the destructor ran. Original hilog has no
observed Release RsNode or read-boot-completed-true log. Continued BootAnimationNode
drawing after animation end therefore does not by itself prove cleanup is broken.

Mini-debug extraction initially stopped on identical-address destructor aliases.
The incomplete symbols-062 directory is retained. symbols-062-r2 completed,
requiring identical assembly for aliased methods. Original ELF was not changed.

## Earlier Concrete Failure In 061

Original accountmgr logs:

- 36.959s: begin creation of base account 100.
- 44.433s: base account creation ends; default activation begins.
- 44.492s: Storage PrepareStartUser returns 0; account 100 unlocked/logged in.
- 44.627s: SendToAMSAccountStart starts OS account 100.
- 44.702s: original foundation reports null tmpSceneSession, scb does not exist.
- 44.703s: StartHighestPriorityAbility fails with 22; SwitchToUser fails with 22.
- 44.706s: original account callback reports errcode 22 for user 100.
- 44.708s: SendToAMSAccountStart fails, then RollBackToEarlierAccount executes.
- 46.699s: WMS-ready successful write appears, after the failed activation.

This establishes an actual account-start failure before SceneBoard readiness.
It does not yet prove that fixing this failure will produce desktop pixels.
Later logs still fail to obtain activated account IDs. SceneBoard process launch
and rendering-command submission are not equivalent to account activation.

The previously extracted init configurations declare 18 service boot events.
Comparing successful SystemSetParameter log entries in 061 finds none for
account.ready and hdf_devmgr.ready, while 16 others have successful write logs.
These log entries do not include values, and absence is not proof of missing
runtime registration/event completion. Additional reserved events/config roots
have not been exhaustively audited. Do not claim account is the only boot gate.

## Reference Alignment

HarmonyMac ports/tests/native-desktop-start.sh uses ordinary aa SceneBoard start,
then explicitly force-stops startupguide. The latter is not adopted here.
The L410 image's original first-boot script retries accountmgr before launching
SceneBoard; current 021/032 integration removes its circular readiness wait and
preserves normal aa/BMS retries. It does not retry the failed account activation
after SceneBoard becomes ready. None of the three local reference trees yielded
a specific bootanimation.finished/boot.completed lifecycle fix in text search.
Linux compatibility remains an application layer, not a boot-completion fix.

## Prepared Integration Change

Original /system/bin/acm SHA256:
42246c7f45238ab753e230fe262629438492d3dc780f2845f8b2d7b68e30f83d.
Its own usage documents acm switch -i <local-account-id>; its imported API is
OsAccount::ActivateOsAccount(int). No CLI execution has been performed here.

commercial-desktop-order-062.py preserves 021/032 normal aa launch and its six
BMS-publication retries inside a subshell, then waits at most 90 one-second
checks for a genuine SceneBoard process and WMS-ready. If account-ready is still
not true, it invokes original /system/bin/acm switch -i 100 exactly once and
propagates the exit status. No service resets are added; existing prefix is kept.
No token/UID change, completion write, OOBE change or force-stop is added.
Original CLI refusal must be retained and diagnosed, not bypassed.

Six offline shell-flow tests passed with mocked commands: existing SceneBoard,
already-ready account, delayed/timeout WMS, CLI error propagation, failed six-try
SceneBoard launch, and forbidden-operation checks. These mocks are not runtime
permission or activation evidence. No numbered 062 runtime was performed.

Next: integrate this change into an isolated candidate, verify exact archive
differences and original security preservation, then perform one bounded boot.
Inspect genuine account callback/result, boot gates, node release, composer source
pixels and physical output. HDF's unobserved ready event remains a separate item.
