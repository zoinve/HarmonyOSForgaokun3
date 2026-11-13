# Original graphical boot 095 — actual SceneBoard Ark/JS startup

## Independently verified outcome

- Actual original SceneBoard PID 3174 was captured at process snapshots 41 and 49. The genuine `hilog -z 400 -P 3174` query at sample 41 returned normally and produced 78,330 bytes of interleaved output. This is diagnostic output, not an application-ready signal.
- Its logs reach `LauncherMyAbilityStage onCreate`, `LaunchAbility`, `JsSceneSessionManager OnGetRootSceneSession`, and subsequent `WindowSceneConfig` processing.
- The same log includes missing `helpsfwk`, `abilityframeworkbroker`/broker ABC and `swingability` modules, undefined HMS exports, a SettingsUtil context/argument error, and clock/cutout configuration warnings. No specific warning has been established as the cause of the black display; continued execution and handled errors must not be confused with an uncaught fatal exception. A normal GC “memory reach limit” record alone does not establish OOM.
- All five genuine QEMU scanout captures (120/360/480/600/650 seconds) remain entirely black at 1280×800. No interactive desktop or physical display is verified. No Foundation critical fault or guest reboot was observed during the bounded run.

Evidence: `original-graphics-boot-095-independent.json`; serial SHA-256 `eddbf0224e12c5610dda3ea2ac900bd6caf81125651feabd265dd376f25da090`. Full independent checks preserved all 12 injected provider ELFs, real ashmem, query helper, initrd, kernel, three original SDK images, 378 earlier native evidence files, the private 8 GiB test volume and lossless PPM/PNG pixels. Guest permissive mode and original service identities remain unchanged.

## Observation limits

Only 50 mode samples and application snapshots through sample 49 were reached within the unchanged 660-second observation bound. There are no raw SceneBoard query headers/end markers for samples 49 or 61; later query absence is not a regex parsing loss or proof that SceneBoard was absent. Other late diagnostic queries also did not reach those phases.

The newly enabled verbose application mapping observer emitted 1,018 PID-3174 diagnostic lines in a 4,822,056-byte serial log. Reducing this unnecessary output is a focused observation change; it has not been proven to explain all observed timing differences. Read-only fault-directory inspection listed a Bluetooth crash file but no SceneBoard file in that listing, which does not prove the application never failed.

## Fresh 096 candidate

- Moves actual main-SceneBoard PID discovery before the verbose service filter and removes SceneBoard from repeated application map dumps. Bounded all-process UID/domain snapshots and genuine original SceneBoard HiLog requests remain.
- No changes to the 660-second bound, capture times, original services, identities, policy, sandbox, profile/DB files, providers 005, EGL/Mesa 009, ashmem or virtual kernel 002. The working canonical read-only `nodev` `/system` and original `/mnt` tmpfs/slave setup remain.
- Offline checks: 096 **2 passed**, parent 095 **2 passed**. Preparation succeeded once: init 853,968 bytes, SHA-256 `d1f58a908bdff89907a58fb2cfd09650f1bd40a2b2594d6917d2739196b235e8`. Runtime and independent verification are pending at this report's creation.

All work remains local isolated WSL/QEMU testing, using all three reference projects. No MateBook/Ubuntu boot, host security or screen-off changes were made. Completed operational experiments and their evidence were not rerun or overwritten. No missing capability or success response was fabricated.
