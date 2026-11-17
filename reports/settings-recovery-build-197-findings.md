# Settings recovery build197

USB work remains paused at181. No target write, install, boot selection or
reboot was performed. Read-only authenticated SSH confirmed the target is
running Ubuntu kernel7.1.0-rc3-gaokun3+.

## Diagnosis

Desktop173 records a real Settings launch for user100 failing with2097152:
the bundle/MainAbility is absent in BMS. Historical153 separately records the
original HAP verifier rejecting the missing signing block with8519742.
Do not represent that historical rejection as a new173 install attempt.

The supplied installer has original Settings BMS/token/code install state.
HarmonyMac migrates supplied state; our minimal seed123 copied SettingsData
databases but omitted this install state. This is a recovery hypothesis, not
proof that restoring it makes the application executable or usable. No token
values, device credentials or USB serials are recorded here.

## Build evidence

Initial197 compiled successfully but stopped during full historical archive
replay because local commercial61-native-016/initrd.img was absent. Partial
artifacts and init.stderr are retained; this attempt is not a successful build
admission and must not be installed.

Revision197-r1 completed:

- Build: /home/zoinve/harmony-virgl-883/commercial61-native-197-r1
- Reports: reports/commercial61-native-197-r1
- Desktop173 runtime binary and source are byte-identical.
- Only outer init and its wrapper hash differ in the full initrd.
- Private persistent headers select /mnt/lab/harmony-settings-data-197/data.ext4
  with UUID b8383c4f-844b-46cc-9d67-34a3745b3f1f.
- Full-allocation, ownership, exclusive-lock, filesystem and loop guards remain.
- Replaying the new overlay onto the hash-verified full173 image exactly
  matches the full197-r1 image. Historical chain equivalence inherits173's
  recorded result; the entire historical chain was not independently replayed.
- New artifacts are not installed or booted. No Settings UI success is claimed.

The independent191-r2 data candidate is still local. Target staging must use
the new directory, fully allocate8GiB, verify hash/UUID and offline fsck, preserve
active165, and pass new workflow admission before a bounded native test.
Use the actual197-r1 build directory for artifact reads, not partial197.
Keep Ubuntu default, automatic return, screen-off timer, image checks and original
HarmonyOS signature/authentication checks. Do not rerun USB175.
