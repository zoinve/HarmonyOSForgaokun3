# Trial003: observation-only candidate006

## Verified return and evidence

- Candidate kernel `7.1.0-rc3-gaokun3-el2` ran with the independent 006 initrd and completed its diagnostic log.
- Ubuntu returned as `7.1.0-rc3-gaokun3+`, boot ID `151d2ca0-706f-4eb9-8edc-f1b0f9093a3d`, different from the previous Ubuntu boot.
- SSH observation began without an initial delay: first probe at about 0.0000014 seconds, confirmed return on attempt18 at 66.243 seconds. This is observation timing, not a measured boot duration.
- All 82 collected raw files independently passed size and SHA-256 verification: 50 prior files plus 32 new cumulative snapshots, not 32 independent tests. New directory: `native-diag-001-83c51d82-3906-4b9b-bc99-80142566c28f`; final snapshot `phase-032.log`.
- The single-use entry is consumed as `harmony-native-diag-006+0-1.conf`. The collector mounted the lab read-only. The only tracked preexisting EFI change was `loader/random-seed`; it was preserved, not restored. Do not claim every EFI byte remained unchanged across boot.

## Findings

The unchanged 005 module plan completed all module requests with status0. The new observation phase reported `DRM_NODE_NOT_OBSERVED`, status124, after its bounded roughly five-second window. The subsequent binding snapshot ran at uptime6.31 seconds. Thus the prior 1.18-second sample being slightly early is insufficient to explain this run; arbitrarily longer delays remain untested.

At the final snapshot:

- Display/GPU clocks, combo PHYs, MDSS, DPU, DSI, DSI PHY, SPI and Himax platform/SPI driver links exist; GPU is bound to `adreno`.
- Both DP controllers have no driver link. Their `waiting_for_supplier` values are **0**, not evidence of a firmware-node supplier wait. Do not equate this field with all DRM bridge/component deferrals.
- Both `aux_bridge.aux_bridge.*` devices and `huawei_gaokun_ec.ucsi.0` exist but have no driver link. No HPD bridge devices were captured. GMU also lacks a driver link; its role is not established as the current blocker.
- Himax input registration persists, including `/dev/input/event2`; physical touch events/calibration are still unverified.
- `/dev/dri` remains absent; enumeration status1. The diagnostic ends with `desktop_verified=0`.

This narrows the next test to the previously source-traced Gaokun UCSI/HPD bridge dependency. `baremetal-native-trial-002-ucsi-package-audit.json` already verified all seven UCSI dependency module files byte-for-byte inside the actual 005 archive. A future fresh candidate can add only that module request while retaining the 006 observation instrumentation and budget. Missing UCSI is still a hypothesis until tested, not a proven sole cause.

## Startup screen-off after a real reboot

`ubuntu-screen-off-001-post-trial-003.json` confirms the timer enabled/active and service Result=success, ExecMainStatus=0 in the new Ubuntu boot. A **read-only** verifier refused all setters and observed the active GDM session already at GNOME power-save mode3 (`state=off`, `changed=false`). The verifier did not itself turn the screen off. This verifies compositor state, not a physical screen observation.

Persistent Ubuntu default is unchanged and no one-shot selection remains. Authentication, identities, trust and watchdog protections were not modified. No HarmonyOS native desktop or hard-lock recovery guarantee is established.
