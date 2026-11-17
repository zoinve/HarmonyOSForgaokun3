# Native 045 — deployment stopped at host-preservation guard

## Completed, without replaying old experiments

- The incremental, complete-line capture candidate was built and independently audited earlier; its overlay is 701,039 bytes, SHA-256 `18d21887be15c02d15dde6b4fcaf8250e0dba1b755fcec3abd7a9c2511909d09`.
- Fresh 045 inventory/stage/installer adapters were added. Their three offline tests failed first because the implementations were missing, then passed (0.022 s). They retain the independent capture-only source audit, three-member overlay, original rendering/service credentials and 64 MiB EFI reserve. The installer never selects or reboots.
- Only the read-only inventory was executed. It failed before producing an inventory or reaching any installation. Preserve `native-presentation-045-inventory-output.txt` and the failed inventory script unchanged; do not rerun that completed attempt.

## Unexpected current host state

Subsequent distinct read-only checks found:

- Current Ubuntu boot ID: `2721607b-0d8e-4538-86bc-60fa499ab6da`, different from the verified 044 return ID `98f25442-d15e-47b4-9a83-388002293439`.
- Kernel remains `7.1.0-rc3-gaokun3+`; ESP remains `/dev/nvme0n1p1`, vfat, PARTUUID `922f37b2-3474-4761-a370-5aa1dcd7c476`.
- Ubuntu is still current/default; no pending one-shot entry was shown.
- `harmony-lab-screen-off-001.timer` is **inactive and disabled**, and its service is inactive. Relevant journal entries show it started at `2026-11-13T01:13:36+00:00` and stopped at `01:19:10+00:00` in the new boot. The actor and intent are not established.
- Device-side staging directory for candidate 045 does not exist.

The timer guard must not be relaxed to force deployment. These intervening changes may be user or other-session work: no attribution, reversal or timer re-enabling was attempted. No 045 staging, EFI installation, one-shot selection, reboot or input injection occurred. No existing logs, entropy, SDK images, identities or security configuration were modified.

Hardware deployment awaits clarification whether to restore the original automatic screen-off setting or preserve the current host state. Any resumed inventory must use a fresh numbered attempt and preserve the first failure. Offline work remains possible without touching the device.
