# Driver, Huawei Share And Kernel Checkpoint

Date: 2026-11-17. This report supersedes build-only progress descriptions where
new runtime evidence exists; it does not alter historical evidence.

## Accepted And Observed

- Desktop and Settings access are user-confirmed.
- The user confirmed Bluetooth connection on candidate 471. This does not prove
  audio playback or all profile behavior. The later volume-down complaint is
  explicitly about the body button, not a Bluetooth headset.
- Candidate 471 loaded the matching OSM L3 module successfully. Real sysfs
  policies covered CPUs 0-3 and 4-7, with nonzero current/min/max frequencies.
  Original frequency-read errors disappeared. Original CPU service dumps still
  contained zeros, so Task Manager display remains unverified.
- Both hardware and original-service evidence must be retained; neither is
  substituted for final UI or physical acceptance.

## Huawei Share

The original 471 log contains 28 failure-word records in
`GetWifiP2pGroupInfo`. This is diagnostic evidence, not proof of a unique cause.
The reference Wi-Fi bridge requires the real P2P control endpoint at
`/data/local/tmp/l410_p2p_ctrl/p2p0`; the current startup creates only the
ordinary wlan0 supplicant path. The reference group-client backend also uses
custom `MAGICLINK`, which cannot be presumed available in stock supplicant.

Ubuntu reports QCA P2P-client/GO/device capabilities. Native availability,
discovery, group connection, address setup and actual file transfer remain to
be verified. No Hi1103 replacement or fabricated control replies were added.
The existing read-only ARM64 iw capture was packaged for future target-only
use. No Ubuntu network changes or target deployment occurred in this step.

`analyze-share-492.py` exports function counts only, not raw messages, device
names, peer addresses or credentials. Its privacy fixture passed.

## Compatibility Kernel

The locally supplied Linux compatibility reference is at revision
`d95fbcecbf780e4086aa90f0c7ad052577121f11`. Its launcher uses memory cgroup v1,
pids cgroups and mount/IPC/UTS/PID namespaces. Existing kernel support was
missing memory cgroup v1, not the entire namespace or Binder implementation.

Independent candidate 490 built Image and matching modules successfully:

```text
CONFIG_MEMCG_V1=y
CONFIG_REBOOT_MODE=y
CONFIG_POWER_RESET_QCOM_PON=y
CONFIG_INTERCONNECT_QCOM_OSM_L3=y
```

The first was disabled; the other three were modules. The exact four-symbol
delta was checked after olddefconfig. Original kernel configuration and source
were unchanged. Existing Binder token/PID checks were retained. The Image is
18,090,496 bytes; binaries and build logs remain local.

The PMIC parent is needed to populate the resin input child used by volume
down; GPIO volume up follows a different path. Built-in registration is not
physical key acceptance. The new kernel and rebuilt modules have not been
installed or booted. Compatibility application execution, memory enforcement,
physical volume-down and Task Manager frequency remain pending.

## Preservation And Publication

Keep desktop173, current471, original images, immutable active data165 and the
experimental data197. Preserve Ubuntu default boot and the active screen-off
timer. Do not rerun completed boot experiments, hash/tree suites or fsck.

Only authored source/configuration and Markdown are published. Images, private
libraries, tool binaries, raw runtime evidence, credentials and third-party
reference worktrees remain local. Source checks are not hardware acceptance.
