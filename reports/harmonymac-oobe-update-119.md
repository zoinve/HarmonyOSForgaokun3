# HarmonyMac OOBE Update 119

Reference review on 2026-11-16. No target boot, mount, image write, settings
database preparation or installation was performed. Native desktop and
interaction remain unverified.

## Pinned Update

Previous reference: f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad.
Fetched origin/main: ed213a08817c642e9b455fb7d8f5271da41631eb.
Commit time: 2026-11-16 07:47:43 +0800.
Subject: Document development OOBE bypass and add reproducible helpers.
Eight files changed, 310 insertions. The previous checkout remains at its
original HEAD; the new reference was inspected separately at
C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-ed213a0.

## Material New Evidence

docs/oobe-development-desktop.md now documents that the historical November 4
direct-desktop candidate also edited BOTH offline SettingsData databases:

- data/app/el1/0/database/com.ohos.settingsdata/entry/rdb/settingsdata.db
- data/app/el1/0/database/com.ohos.settingsdata/entry/rdb/settingsdata_slave.db

It set SETTINGSDATA.device_provisioned to string 1, and
USER_SETTINGSDATA_SECURE_100.user_setup_complete to string 1. The document
separately records install-list removal and renaming the original guide HAP
as historical attempts, not a recommended replacement for runtime stopping.
The historical noobeboot110 stopped the guide once at uptime 116 seconds.

This supersedes treating the previously public force-stop script as the whole
historical candidate preparation. It supplies a real previously missing state
difference; it does not prove that the state edits alone caused success.
The new documentation says guide reentry still occurred after those edits and
the final runtime force-stop remained necessary. It explicitly distinguishes
local first-run state from commercial activation and TEE/SoC attestation.

## Relation To Local Evidence

Run 116 read device_provisioned as 0 and kept isOobeEnable true. Audit 117
established that active OOBE plus a matching trust-list entry reaches recovery.
The newly documented reference initialization edits are relevant to that
branch. However SCBOobeManager.initDeviceProvisioned also has an existing
OobePreferences cached-value path before its SettingsData fallback, and
isOobeActivated can include OTA state. Therefore editing two DB keys is not
proof that this existing target data layer will take the inactive branch.
Do not silently change cache values, suppress recovery or claim activation.

## Tool Review And Verification

ports/tools/prepare-oobe-settings.py reads an offline, checkpointed input DB,
copies it to memory, updates only the two first-run keys and creates a NEW
output DB. It refuses sidecars, missing schema and existing output. It does
not mount an image, replace guest files or install startup scripts. Its output
metadata is not a substitute for guest UID/GID/mode/SELinux labels. Master and
slave handling and complete backups are the caller's responsibility.

ports/tests/enter-development-desktop.sh waits for the actual guide process,
settles, stops it once and observes exit. Its success message proves only
observed process exit; it does not establish sustained absence or desktop
visibility. It does not automatically modify existing startup configuration.

Executed in the separate reference checkout using WSL Debian:

- python3 scripts/test-oobe-tools.py: 2 tests passed.
- python3 scripts/check-repository.py: 172 source files, hygiene/links/syntax
  passed.

Initial tests failed because Windows checkout converted shell files to CRLF.
Re-extracting this newly created reference checkout with core.autocrlf=false
restored original LF and allowed both checks to pass. These are offline
synthetic fixtures and static checks, not deployment evidence. The upstream
commit itself explicitly reports no new VM run or active-image write.

## Scope Boundary

No longer assume reference package-state parity from the unchanged vendor
image alone. Conversely, do not blame an image mismatch: the documented
difference is preparation of the development data/root layer.

Reproduction of those state edits would change local initialization status,
which prior work preserved rather than fabricated. This review does not
authorize or apply that change. Any later authorized development-copy
experiment must preserve the original images, back up complete offline data
including sidecars, inspect the actual schema/user/cached state, retain file
metadata, use a new numbered reversible layer, and verify original callback
behavior plus real desktop pixels and interaction. No package removal,
authentication bypass or commercial activation success follows from this
documentation.
