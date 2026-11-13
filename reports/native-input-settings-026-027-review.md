# Touch rotation, detachable input, Settings — native 026/027

## Status

Two new physical trials were run once each and automatically returned to Ubuntu. Input hardware fixes are present in candidate 027. **The Settings main window is not yet verified working.** Stable 120 FPS remains a later, unachieved target; it was not substituted with a 120 Hz mode claim.

### 1. Real touchscreen orientation

The original Gaokun Himax device tree still transformed raw input into portrait coordinates although the composer now exposes a 2560×1600 landscape screen. Candidate-local DTBs remove only `touchscreen-swapped-x-y` and add `touchscreen-inverted-y`, retaining the existing X inversion and raw sizes. This implements the inverse of the actual clockwise display transform, rather than relabelling axes.

- Native gesture diagnostics now report `x=0:2559 y=0:1599`.
- In 027 the original MMI sends the real kernel gesture to SceneBoard's 2560×1600 lock window. The original unlock event follows at approximately 44.74 seconds.
- Disposable corner/midpoint mapping tests verify the coordinate relationship and exact two-property delta. This is not a physical finger alignment test; corner taps by a human remain unverified.
- New DTB SHA256: `5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016`. Each entry references its own DTB. Shared diagnostic 015 and Ubuntu device trees were not changed.

### 2. Actual detachable keyboard and touchpad

The target kernel already contained the matching drivers, but the diagnostic bootstrap had not loaded the USB PHY and multitouch modules. Loading `phy_qcom_snps_femto_v2`, `phy_qcom_qmp_usb`, and `hid_multitouch` succeeds in both target boots.

USB `12d1:10b8` now enumerates keyboard, mouse and touchpad interfaces. In 027, original `multimodalinput` PID 229 holds actual `/dev/input/event6` (keyboard) and `/dev/input/event9` (touchpad) descriptors throughout observed samples 3, 9 and 11, in addition to Himax event2. An explicitly labelled synthetic Meta+I key sequence written through the real keyboard event device reaches original SceneBoard at approximately 50.23 seconds. It did **not** establish that the Settings shortcut is supported or working. USB hardware-generated key presses, touchpad motion and gestures were not manually exercised.

### 3. Settings remains unresolved

Read-only inspection of the original Settings HAP confirms bundle `com.huawei.hmos.settings` and main ability `com.huawei.hmos.settings.MainAbility`. Settings extension processes do start, but this is not proof of the main window.

The 026 observer's original `aa start` request is explicitly rejected by original Foundation:

> Caller has no resolvable parent/hap token and lacks background-start permission, REJECT.

The numeric result is 22. The CLI's generic bundle-not-found explanation is misleading here: server logs identify the actual background-launch check. This diagnoses the **observer's test request**, not the user's desktop click failure. No caller token was fabricated, service impersonated, permission bypassed or check disabled.

027 removes that invalid launch probe and instead sends ordinary keyboard input through MMI. SceneBoard receives the key events, but no Settings main-ability launch/window success is established. Next work must capture an actual desktop Settings launch request and its original caller's result, with useful UI/window diagnostics; do not “fix” the unrelated privileged diagnostic request.

## Evidence and preservation

- [Independent verification](native-input-settings-026-027-verification.json): all 118 snapshot SHA256 values checked, actual service UIDs/domains preserved, 12 permissive SELinux samples per trial, original namespace root stable, original graphics stack retained.
- Original images remain read-only; all three image hashes match after each boot. Target data remains the isolated 3 GiB RAM ext4 volume.
- 026 returned as Ubuntu boot `a492d989-a4ea-42c4-ba33-e18de1548897`; 027 returned as `ecf7cc9d-eebb-4c87-83a7-96fe3fca93e2`. Ubuntu remains default, one-shot selection clears, automatic screen-off remains active, host LSM remains `capability,landlock`.
- Installer 026 reclaimed only the unreferenced duplicate EFI initrd for completed 016; installer 027 reclaimed only completed 018's unreferenced duplicate. Both were verified against retained originals and journalled before deletion. Original candidate payloads outside EFI and numbered logs remain. All other 81/83 static EFI files respectively match after normal random-seed rotation, which is separately recorded.
- Each 026/027 trial produced 59 immutable raw snapshots. Never repeat these operational trials or overwrite their evidence.

Reference continuity: matching native Gaokun Linux kernel/device tree and its working USB drivers; HarmonyMac original-service graphics and ashmem adaptations; L410-HarmonyOS-Adaptations storage/ABI work; L410-Linux-Compatibility-Platform service/dependency architecture. No reference source or Ubuntu driver configuration was changed.

## Deferred performance work

025 moved the native-window copy to real GPU dma-buf/FBO blits with native fences. Its bounded startup submission median was 3.733 ms, but cached CPU composer rotation still took a median 27.106 ms. Those are stage measurements, not presentation FPS. The actual 120 FPS requirement remains in [the target](native-120fps-target.md), pending GPU composition and sustained real presentation measurements after these higher-priority usability issues.
