# Native diagnostic trial 002 — candidate 005

## Verified evidence

- Reboot command returned 0. SSH observation began at 0.0000012 seconds without an initial sleep; attempt 12 observed returned Ubuntu at approximately 49.36 seconds. This is observation timing, not the exact boot duration.
- Ubuntu boot ID changed from `a1deb268-f7a1-4774-95d1-ee9a28e1dac8` to `885ef37b-baf8-471d-9b7b-f2ed7e46da91`; returned kernel is `7.1.0-rc3-gaokun3+`.
- Candidate ran `7.1.0-rc3-gaokun3-el2` with the 005 initrd. New diagnostic directory: `native-diag-001-204aa1fb-7790-49ed-97d4-216f31232c7d`.
- All 50 collected raw files were independently checked against manifest byte lengths and SHA-256 hashes: 30 new snapshots and 20 historical trial-001 snapshots. These are cumulative snapshots, not 30 independent phase logs.
- Final snapshot contains one NUL byte from the device-tree model property; raw bytes are preserved unchanged.
- All 12 explicit module commands returned status 0. Both binding snapshots and kernel-log command returned 0. Enumeration returned 1 because `/dev/dri` was absent.

## Hardware findings

The post-load snapshot at approximately 1.18 seconds shows actual driver links for display and GPU clock controllers, both combo PHYs, MDSS, DPU, both DSI controllers and DSI PHYs, and GENI SPI. `spi0.0` is bound to `himax-spi`.

`Himax Capacitive TouchScreen` registered at approximately 1.158 seconds as input2 with handler `event2`. `/dev/input/event2` exists. This establishes driver binding and input-device registration, **not physical touch events, calibration or HarmonyOS input integration**.

No DRM class device or `/dev/dri` was present at enumeration. Final snapshot contains `NATIVE_DIAGNOSTIC_END desktop_verified=0`; successful module commands and platform driver links do not establish completed DRM component binding. No physical display activation or HarmonyOS boot was verified.

## Return and preservation

- `harmony-native-diag-005+0-1.conf` is consumed.
- Read-only Ubuntu comparison confirms persistent default remains the standard Ubuntu entry and `LoaderEntryOneShot` is absent.
- The collector mounted the lab partition read-only with evidence-preserving options.
- The collector found exactly one changed pre-existing EFI file: `loader/random-seed`. Boot-time seed rotation is consistent with systemd-boot behavior; it must not be restored to the stale seed. Do not describe all pre-existing EFI files as unchanged after this reboot. No other tracked pre-existing EFI file hash changed.
- Successful Ubuntu return does not prove diagnostic unmount success or hard-lock recovery.

## Next investigation

Read-only Ubuntu comparison (`baremetal-native-trial-002-ubuntu-comparison.json`) shows working DRM card0, renderD128, DSI-1 and two DP connectors. Normal boot logs complete component binding at about 1.30 seconds, later than candidate 005's enumeration. Ubuntu also has bound auxiliary HPD bridge devices; these were not included in 005's binding observations. Distinguish insufficient observation time from a missing supplier before changing the candidate. No additional reboot has been requested during this review.
