# Share runtime checkpoint 550

Date: 2026-11-17. Current-state update; earlier evidence is unchanged.

## User-observed517 failure

The user confirmed Share still failed and manually restarted the device.
Ubuntu return was observed at 04:09:22 UTC, and guard529 confirmed the Ubuntu
current/default entry, no one-shot entry, active screen-off timer and an
unmounted lab partition. Eight retained runtime evidence files were retrieved
with transport integrity checked; no historical filesystem suite was rerun.

Analysis528 found real p2p0 creation but supplicant exit255 and no PONG.
Read-only inspection530 of data197 found a 237-byte supplicant log with two
configuration-parse error records. Original bridge group log was absent.
These selected logs can be cumulative, not run-isolated. No raw credentials
or peer identifiers were exported, and active data165 was not accessed.

The original CPU service still reported zero frequency fields despite real,
positive qcom-cpufreq-hw policy values. Physical volume-down operation is
unaccepted even though pmic_resin is enumerated.

## Confirmed config defect

The no-config-write upstream build does not register update_config, even when
its value is zero. QEMU regression531 used the actual public517 config and
a deliberately nonexistent driver, without opening a radio. It reproduced
the update_config=0 parse failure. Removing that one field passed parsing and
reached the expected unsupported-driver error. Candidate532 packages this fix;
integration533 passed three tests and checked the unsupported field is absent.

## Candidate532: return not verified

532 was installed and booted once at 04:16:02 UTC. The existing kernel490 was
reused unchanged. Installation retained desktop173 and Ubuntu default, archived
the retired517 entry, and left 37,392,384 bytes free on the ESP. Only unreferenced
458/471/502 ESP overlay copies were removed in520/534 after checking their
existing backups. Original images and active data165 were not written.

The restricted native SSH endpoint authenticated at 04:17:51 UTC and reported
growing original logs. This is not desktop, P2P, group or transfer acceptance.
Waiter537 terminated after its 1100-second observation window without seeing
Ubuntu. A fresh check549 at 04:36:27 UTC found Ubuntu SSH and the last native
endpoint unavailable, with no newly discovered native endpoint. The management
computer's network adapters remained up. Neither a reboot cause nor the actual
device screen is established. No boot retry was requested.

Do not retrieve532 logs until Ubuntu identity and return can be verified. Do not
rerun532 to replace missing evidence. The user's screen-state confirmation is
needed to distinguish a stopped reboot, black screen and device network loss.

## Prepared next candidate, not installed

The separate P2P backend543 uses official hostap2.12 commit
831364bf02710ad09c2f27d3efa92abeeb5634c0. Provenance/CLI regression545 checked
ancestry of fixes65d865e6 and b0b23f99, accepted -f and parsed the corrected
public config. The original ordinary-wlan binary is not replaced. The MAGICLINK
adapter uses the upstream real WPA handshake with its updated2.12 function
signature; it does not synthesize connection events.

Candidate546 combines that backend with the unchanged kernel/module bundle and
a bounded private memory/pids controller probe. It is built, not installed or
booted. The earlier542 build is also uninstalled and is superseded by546.
Integration548 passed three tests and checked probe wiring, matching modules,
the corrected public config and embedded backend identity.

The probe affects only its own child, uses a 32MiB memory limit and pids.max=1,
requires actual kernel OOM/fork-denial counters, and caps its wait at ten seconds.
It uses private mounts, does not change target /dev mounts and does not assign
HarmonyOS services to test cgroups. Revision547 compiled the ARM64 helper and
passed ten ASan/UBSan numeric-parser cases after making its child gate immune
to SIGPIPE. It has not demonstrated native resource enforcement yet.

The reference launcher needs real /dev/memcg and /dev/pids control files;
previous502 mount evidence showed CPU/blkio hierarchies, not these mounts.
Kernel490 config includes memory v1, pids, namespace and seccomp support, but
that alone does not establish mounted controllers or platform app execution.
No Mali/Hi1103 driver imports, vendor memory-stat placeholders, fabricated
readings, token-check removals or unique-identity replacements were introduced.

## Remaining Acceptance

Real P2P PONG, original bridge attachment, group formation and a physical file
transfer remain unverified. Compatibility-platform app execution/resource
enforcement, Task Manager frequency, physical volume-down, multitouch, acoustic
audio and120Hz remain pending. USB work is preserved and paused.
The overall hardware-driver goal remains active and incomplete.
