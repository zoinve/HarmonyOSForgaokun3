# Settings routing follow-up177

Read-only analysis on 2026-11-16. No packages, target configuration or signature
checks changed. Three focused analysis tests passed. Native173's complete
retrieved-file manifest was checked before reading its runtime log.

## Evidence

`settings-routing-177/result.json` records compact original module declarations,
source-metadata SHA256, native run identity and conservative runtime observations.
Its line indices count Python splitlines records, not necessarily newline-only
physical log lines.

- Main Settings declares `com.huawei.hmos.settings.MainAbility`, visible true.
- PCSettings declares `MainAbility`, visible false, with home and
  `action.settings.menu.v1` skills. Audio, wired-network, application-management,
  trackpad, keyboard and mouse abilities declare settings-menu integration.
- PCSettings MainAbility has no explicit exported field in the captured metadata.
  Missing is recorded as unknown, not converted into exported true or false.
- PCSettings preceding-central-directory bytes contain `<hap sign block>`;
  Settings bytes do not. Marker detection is not cryptographic verification.
- Native173 restores a PCSettings access token for user100. Its BMS warnings
  concern `com.huawei.hmos.pcsettings_-3`, not an explicit user100 bundle
  absence. Neither observation independently proves a usable installed ability.
- No PCSettings ability launch or replacement for main Settings is verified.

Main Settings' original verifier rejection and correlated absent-bundle launch
failure remain established by155/173. PCSettings is not a demonstrated repair.
Do not redirect the desktop shortcut, change package identity, or disable signing
based on these declarations. An authenticated installed-ability query and an
actual original-service launch are required before claiming any PCSettings UI.

## Current Hardware Snapshot

`input-usb-147-20261116T095027501877Z/result.json` is a fresh Ubuntu-only snapshot:
Himax touchscreen, Huawei keyboard and touchpad enumerate. Both Type-C ports
report host data role; port0 is source and port1 sink. No USB storage enumerates.
No input-event contents or USB serials were read. This rules out current device
data role as the observation, not a historical role switch or other USB fault.
It is not HarmonyOS HDI/UI acceptance.
