# Settings diagnosis201-204

USB work remains paused at181. Working desktop173 and active data165 are not
replaced. Settings has NOT been verified working.

## Captured launch refusal

Experiment201 made one original aa request with unchanged root credentials:
com.huawei.hmos.settings / com.huawei.hmos.settings.MainAbility, module pc_settings.
The original AMS refused it at its first-screen-unlock interceptor, result
2097253; aa displayed10108101. The lock check used user0 and defaulted to locked.
CLI exit0 is not semantic launch success. This root request does not establish
the result of a real user100 desktop click. Do not bypass the interceptor or
impersonate application credentials. Original aa start help has no documented
user selector; -U means URI, while dump's -u is not a start option.

Evidence: commercial61-native-201/runtime-evidence/raw/settings201-start.log;
interactive-hilog030.log around81054-81088; original-aa-203/result.json.

## Account lifecycle comparison

Read-only analysis204 compares preserved173 and201 logs and records their
hashes and matching line numbers without exporting account identities/tokens.
Baseline173 records default account activation, user100 storage unlock and
an AMS account-start request. It also records an account-start callback error22;
do not portray the baseline lifecycle as entirely healthy.

Candidate201 has no matching default activation/storage-unlock/AMS-start event
in the captured hilog. Foreground-account queries continue failing later in
the capture. Its accountmgr starts with pid1025 and then pid3131. Kernel/init
evidence explicitly records stop_service and signal9 at about27.8s, so this
restart must not be labelled an unexplained crash. Existing desktop-order063
contains an original-service stop/start retry when account.ready is not true.
The relationship between this retry, missing initialization events and Settings
is not established. systemAccounts parsing errors appear in both runs and are
not independently diagnostic. Device-manager's cached user100 is not proof of
an active account-service session.

Next investigation should establish why original account initialization differs
and capture a genuine user100 launcher request. Do not guess aa user flags,
fabricate account/unlock state, or import foreign activation identities.

## Preservation

201 completed one boot and returned Ubuntu. Retrieved183 evidence files matched
remote hashes. Independent202 inspection reports fsck0/clean, matching native
boot marker and successful native teardown: four aliases removed, none left,
inner/backing/outer flush succeeded. Previous197 teardown123 did not recur;
its cause remains unproven, not fixed by this observation.

Current isolated candidate SHA256:
e7e18b21f4e1d0d6a4acd652edc13b64c0ab4f3540ea6ddb155ea107f4e57fb4

Active165 SHA256 remained:
36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce

Original image hashes, Ubuntu default and enabled/active screen-off timer were
preserved. Retained experimental entries are173/201. No stable desktop frame
or Settings window was accepted for201. A future native experiment needs a
new number and the current candidate hash; never rerun197/201.
