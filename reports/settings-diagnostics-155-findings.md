# Settings launch failure: evidence 153, analysis 155

## Confirmed failure chain

Evidence: `commercial61-native-153/runtime-evidence/raw/interactive-hilog030.log`.
All 188 retrieved evidence files were rehashed before analysis.

- Line 52423: the original HapVerify reports `No HAP Signing Block before ZIP Central Directory`.
- Line 52426: BMS names `/system/app/Settings/Settings.hap` as the rejected package.
- Lines 52427 and 52432: signature-info error `8519742`; system Settings installation fails.
- Four later HarmonyKey requests target `com.huawei.hmos.settings/com.huawei.hmos.settings.MainAbility`.
- Each request correlates, by foundation trace ID, with an absent bundle for user 100 and ability-request error `2097152`.
- One example is November 16, 2026 at 12:41:26 local time, lines 391815-391847. The initial installation logs precede wall-clock synchronization and display January 1; that timestamp alone is not evidence of an expired certificate.

This explains the captured Settings launch failures before any Settings UI process starts.
It is not a touchscreen failure or evidence that Settings crashed after opening.
Earlier SettingsData provider initialization failures are not used as the cause.
Not every possible Settings entry point or other application launch was tested here.

## Read-only source-package inspection

`settings-diagnostics-155/result.json` records original module metadata, package hashes,
and the 32 bytes preceding each ZIP central directory. No package was executed or modified.

- Settings: bundle `com.huawei.hmos.settings`, version `6.0.0.412`, SHA-256 `299cfd91df8456b6f46d6fe4c3056e38f9d7f2b04e66466e16fa3d95768bed5c`.
- PCSettings: bundle `com.huawei.hmos.pcsettings`, SHA-256 `eb91513978a1d8e912e47cb0cfadc291bc0947c1e3aa3ef889fa84b1189e99f4`.
- These are distinct packages. PCSettings includes audio/network/trackpad/keyboard/mouse abilities; its presence does not repair installation of the main Settings package.
- Offline ZIP inspection is not an independent cryptographic signature verification. The authoritative signature rejection above is from the original native verifier.

Do not substitute package identities, disable signature checks, or claim a repair.
The next repair investigation is to locate an intact, correctly signed Settings package
matching this image/build and its legitimate trust configuration, preserving originals.

## Real-time debugging status

No live authenticated debugging connection has been verified.
The native 153 run acquired WLAN address `192.168.10.210` (phase-172 line 85521),
so absence of all network connectivity is not the demonstrated obstacle.
The original `/system/etc/init/hdcd.cfg` is recorded in the JSON report:
it defines conditional startup, the shell identity and original permissions.
An initialized native token or the separate hdc credential socket is not evidence of a running HDC transport.

Historical experiment 920 explicitly observed `non developer mode, hdcd does not start`;
this is historical evidence, not a fresh measurement of developer mode in native 153.
Do not repeat that experiment, force developer mode, change authentication, or expose an unauthenticated shell.
Prefer an authorized original HDC connection when available. Any alternative diagnostic
transport needs authentication, restricted commands, bounded lifetime and preservation checks.

## Verification

- `test-settings-analysis-155.py`: three tests passed, including unrelated-provider exclusion and trace/worker correlation.
- Native 153 returned to Ubuntu; default boot, 175 prior EFI files, original images,
  firmware and enabled/active screen-off timer passed preservation verification.
- No additional operational boot or target change was made for analysis 155.
