# Radio result 266 / 283

2026-11-17 Asia/Shanghai. User requested autonomous tests while asleep.

## Observed

- Returned to Ubuntu, observed at 01:08:34. No additional reboot requested.
- Retrieved18 files read-only with noload; source partition not replayed.
- Correct Settings197 backing identity accepted; original HDF configuration
  and QCA vendor binds succeeded. Broker listened under original UID3021 policy.
- Original blue_host ran and registered hci_interface_service successfully.
  HDF rewrites argv[0] to blue_host; analysis274's literal executable-path
  process count0 is not evidence of a missing host. Actual process samples
  include blue_host -i5 -n blue_host and original service registration logs.
- Bluetooth HDI lookup now succeeds, but vendor BT_OP_POWER_ON fails. Broker
  logged no accepted channel attempts. No real HCI commands/completions yet.
- Read-only supplicant SCAN_RESULTS reported4 BSS on all3 samples.
  Nearby Wi-Fi UI acceptance remains unverified; no Settings scan request
  occurred in this unattended run. Do not infer the IPC ABI cause yet.
- Original services read HUAWEI MateBook E Go product name and GK-W7X model.
  Screen display and M1010 hardware-version display were not independently
  verified. Current image capture was encoded to screen-281.png, but the
  image-viewing tool rejected viewing; do not claim visual inspection.

## Remaining name

Original provider logs identify the remaining persisted reference name at:

    datashare:///com.ohos.settingsdata/entry/settingsdata/USER_SETTINGSDATA_SECURE_100?Proxy=true&key=settings.general.display_device_name

The value is still the reference L410 name. No SQLite edit was performed.
Find a supported provider/UI write path under original permissions. Physical
serial/UDID/authentication logic must remain unchanged.

## Candidate276

- Same radio behavior as266, adds HiLogPrint diagnostic logging to vendor
  power-on failures. No false-success callback, packet translation or original
  service permission changes.
- Compiled and installed, started once. Original read-only endpoint authenticated
  at01:15:24. This is not Bluetooth or Wi-Fi UI acceptance.
- Keep desktop173, original images, active165, Ubuntu default, screen-off timer.
- Collect with collect-radio-276-279.py after return; exclude235/253/262/266.
- Independent WSL test275 confirms pathname Unix sockets can cross network
  namespaces there; this alone does not prove target-kernel behavior.

## Storage

Compression282 compressed22 completed logs from253/262/266, saving342247213
bytes. Contents verified lossless; no additional per-file hash table created.
Use compress-historical-logs-226.py:open_log for these now-compressed logs.
No disk hash/fsck/tree-comparison suite rerun.
