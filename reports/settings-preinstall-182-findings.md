# Settings investigation and USB checkpoint182

USB work is paused at the user's request. Existing 175/176/178/180/181
sources and evidence remain in place. Candidate176 has not been installed or
booted; node planner180 has not been integrated. No USB changes are made here.

Read-only debugfs inspection of the supplied original system image confirms
/system/etc/app/install_list.json explicitly lists /system/app/Settings,
/system/app/PCSettings and /system/app/SettingsData, all removable: false.
This rules out a missing entry in that specific source preinstall list,
not all possible runtime configuration or installation failures.

Historical native153 evidence, analyzed in155, records the original HAP verifier
rejecting Settings.hap with No HAP Signing Block before ZIP Central Directory
and error8519742. Native173 independently records the November16,2026
16:43:25.688 local Settings launch, followed by a missing bundle for user100
and ability error2097152. Native173 does not contain a new install rejection.
Its authenticated restricted query also observed the absent Settings bundle.
These are historical observations, not a current live debugging session.

The observed failure occurs before the Settings UI starts. Touch input or a
Settings UI crash is not the demonstrated cause. A certificate/trust-list edit
is not established as a remedy for the reported missing signing block.
PCSettings is distinct and has not been verified as a usable replacement.

No fix is claimed. Investigate original package provenance and any matching,
legitimately signed Settings package or original packaging mechanism next.
Do not clear persistent data, re-sign privileged Settings, disable verification,
or redirect shortcuts based on this evidence. No target writes or boots here.
