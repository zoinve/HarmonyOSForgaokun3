# Settings native recovery197-200

## Actual result

The isolated original-install-state candidate completed one native boot and
returned to Ubuntu. Original BMS main and slave databases retained Settings
for user100, enabled, with MainAbility enabled and matching application-token
references after that boot. This is stronger than finding rows in an unbooted
seed, but is NOT a successful MainAbility launch or a usable Settings window.
No candidate Settings start request was captured. Desktop/UI acceptance remains
incomplete. Do not replace active desktop-data165 with this candidate.

USB remains paused at181; no USB175/176 boot was repeated.

## Native evidence

- Native run: commercial61-native-087-76d33584-471a-4e78-bab5-e417a6d5c30b.
- Build and operation records: reports/commercial61-native-197-r1.
- Complete29-archive reconstruction, reproducible binaries, non-PID1 guards,
  and18 focused test scripts passed. Desktop173 runtime and source were copied
  byte-for-byte; only outer init/wrapper changed in the full initrd.
-182 retrieved files matched the remote hashes, with the original read-only,
  noload and privacy checks. No completed native experiment was rerun.
- Pinned authenticated restricted SSH connected at192.168.10.207. Logs grew;
  arbitrary shell was refused. The first Settings snapshot/follow emitted no
  selected launch/rejection event. A later follow connection was refused.
  Neither observation establishes application absence or successful UI launch.
- No full-output PPM capture is present in this run. The original launch bridge
  reports OOBE114_MISSING_EXISTING_SCENEBOARD at its early check; a later sample
  briefly lists a SceneBoard PID. This is not a stable desktop acceptance.

## Original-service Settings state

Source and post-boot comparisons are in reports/settings-live-state-200.
All four queried BMS/token SQLite copies passed integrity checks. Nonempty WAL
was copied and read with SQLite, not discarded or header-normalized as if empty.
Private temporary copies were removed; raw token values were not exported.

Both post-boot BMS databases contain com.huawei.hmos.settings, user100,
UID20020028, enabled=true; com.huawei.hmos.settings.MainAbility is enabled
in module pc_settings. Each main/slave user100 token reference matches exactly
one corresponding application-token record. These selected fields match the
supplied preinstall source. This is not independent signature verification.

Two native preinstall attempts finish with8520194 alongside the explicit
message App is exist in user(100). Subsequent event callbacks use userId-1/uid-1.
Those callbacks must NOT be misreported as proof that Settings is absent for
user100: the original service message and persisted user100 rows contradict
that inference. No reliable symbolic mapping of the commercial error number
was established; do not substitute a public-branch error name by guesswork.

Relevant lines in interactive-hilog030.log:60382/60386/60411 and
115820/115831/115933. The prior173 absent-bundle launch2097152 and historical153
HAP-signature rejection8519742 remain separate historical evidence. They are
not fresh197 launch/signature failures.

## Storage And Preservation

Candidate: /mnt/lab/harmony-settings-data-197/data.ext4
UUID: b8383c4f-844b-46cc-9d67-34a3745b3f1f
Initial SHA256: f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce
Post-boot SHA256: 41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6

Native data mount, original-init handoff and fresh boot markers are observed.
Exit cleanup reports PERSISTENT172_FINISH status=123 target_reaped=1, without
the required successful flush marker. Code123 identifies allocation/load-plan
failure, not a demonstrated unmount syscall failure; its detailed cause is not
yet established. An init mountinfo sample is NOT the finish worker's mountinfo.
Do not guess that its row count or duplicate paths explain this failure.

Independent read-only199 inspection confirms fsck0, clean filesystem and the
matching native boot marker. Inspection did not change candidate bytes. This
does NOT retroactively prove successful native teardown. Full native storage
acceptance is explicitly false; no repair or journal replay was requested.

Active desktop-data165 SHA256 before deployment, after deployment and after
native boot remains36246b8dc557f2385a8491e3e6d32aaddccad2974f0603f127c335f2b38a9dce.
All four original image hashes, firmware and Ubuntu default were verified.
Screen-off timer is enabled/active; LAB is unmounted. Boot-entry retention
archived and removed175's entry, retaining173/197 plus Ubuntu/manual. Shared
payloads were not removed. Normal loader/random-seed change is accounted for.

Transfer failures198/r1/r2 are retained. The root-filesystem staging attempt
refused insufficient reserve before creating a payload. Direct streamr1 failed
because the local private source required WSL root; its all-zero preallocated
file was archived, then verified byte-identical before/after hole-punching.
Revisionr3 streamed as WSL root into the new LAB candidate, fully allocated8GiB,
verified the expected hash/UUID/fsck0 and preserved active165. No host security
settings were weakened to perform the transfer.

## Next Acceptance

Keep197 as completed evidence and never rerun its operational boot. A new
numbered experiment must pin the actual evolved candidate state, diagnose
the finish-worker plan failure, and request Settings once through original
aa/AMS under original credentials/checks, collecting return/process/window
evidence. Retain the usable173 baseline and active165. Do not fabricate bundle
rows, re-sign the HAP, weaken verification, redirect to PCSettings, or resume
activation/USB experiments. The original services created first-boot state;
its existence does not justify importing foreign account/activation identity.
