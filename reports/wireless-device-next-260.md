# Wireless And Public Device Information

## User Acceptance And Priority

On2026-11-17 the user confirmed Settings is accessible and switched priority to
Bluetooth enablement, nearby Wi-Fi discovery, and actual device name/model.
Stop Settings-open repair. Preserve desktop173, active165, candidate197, Ubuntu
default, original images and paused USB181. Do not resume disk validation suites.

## Current Evidence

253 returned to Ubuntu, observed at2026-11-16T16:28:49Z. The observation does not
prove the reboot cause.256 retrieved15 files from this same boot without journal
replay; no further boot was requested. Keep historical Settings acceptance fields
unchanged. The new user confirmation supersedes the earlier operational priority.

257 reads real public firmware fields: HUAWEI, GK-W7X, M1010; DT Matebook E Go.
Ubuntu enumerates ath11k_pci Wi-Fi and hci_uart_qca hci0, neither rfkill-blocked.
This is backend enumeration only, not HarmonyOS UI acceptance.

In253/runtime-evidence/raw/phase-207.log:
- line1359 records hci_uart module load status0; line1387 enumerates hci0.
- line1647 records Wi-Fi phy namespace migration status0.
- line51812 records supplicant start status0, with real namespace pin evidence.
- line96989 records a real IPv4 interface address; do not reproduce SSIDs or MACs.

In253/runtime-evidence/raw/interactive-hilog030.log:
- line116847: HDF reports hci_interface_service not found.
- line116852: Bluetooth hdiInit failed:2; line134112: startup_timer_expired.
- line401518 records actual Settings navigation into Wi-Fi.
- line401772 records Settings scanAp result false. This JS field alone is not a
  complete native scan result; later native StartScan calls are present.
- line402016 records native GetScanInfoList size1.
- line407306 records failed IWifiScanCallback IPC delivery, error29189. This is
  evidence of callback failure, not proof of an ABI mismatch or why only one BSS
  was returned. Need actual supplicant BSS count and current client parcel ABI.

259 reads the original chip HDF configuration: it contains blue_host,
libbluetooth_hci_hdi_driver.z.so and hci_interface_service. The original vendor
implementation depends on libbt_vendor.z.so, whose hardware path is /dev/hwbt.
Thus merely registering the absent service cannot establish QCA functionality.
Existing native-qca-vendor-022.c and native-qca-broker-022.c are possible real H4
backend starting points, not proof of compatibility with the current HDI ABI.
Use all three reference projects; do not import Hi1103 initialization success
placeholders or replace original authentication/UID checks.

## Implemented But Not Deployed

build-device-profile-258.py produces a377389-byte minimal overlay derived from253.
Only early-hardware093.sh changes: actual firmware model is retained; product
name becomes HUAWEI MateBook E Go; hardware version comes from DMI product_version.
Original serial/UDID logic and desktop runtime remain unchanged. sh -n succeeded.
No full image clone was created. No installation or boot occurred.

The persisted user-editable device name may override the product default; its
supported Settings/provider migration remains pending. Do not edit arbitrary
SQLite records or claim the L410 display name is already removed on hardware.

## Next Implementation

Find why blue_host is not loaded/published despite the original HDF node. Integrate
its original service path with a real QCA controller transport, preserving process
credentials and bounded teardown. For Wi-Fi, distinguish real BSS scan population
from scan parcel decoding and dead callback handling before changing the bridge.
Install the public-device overlay with the next bounded radio candidate, using
the existing single-boot workflow and entry-retention guards, not a new full clone.
