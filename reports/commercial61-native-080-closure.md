# Native Wi-Fi power dependencies 080 outcome

One completed operational boot, 2026-11-15 03:55:14 to 03:59:21 UTC:
commercial61-native-080-d912196b-e188-4419-8293-50745030571c.
Returned Ubuntu boot ID bc7b2268-1d22-452c-991b-45856fe8c995.
Desktop, network association and original OOBE completion remain unproven.

## Exact change and tests

The only archive member changed from full 079 is outer init. Original firmware,
bootstrap, original services/configuration, diagnostic script and network
namespace flags remain byte-preserved. Original bootstrap SHA256 remains
c136b0522ea34a167f372fd5df35b31b38cc0b26ce512e6c1b561aca67004dd7.
The own inherited observation service retains its internal 079 name/marker;
this is intentional and not a claim that 079 operational evidence was rerun.

The exact 355,832-byte overlay SHA256 is
04b4c67499290eb93d28744b7841eeabd551b495edba6debef806c5f762ac709.
Its parent is hash-matched 079 overlay
2402130b010ff40232102f5fc8d700ca31184ad84f61a6e53b0372f0239b7571.
The installed chain appends 080 without deleting shared payloads.

Admission validates init-only delta, ordered bounded module loads, packaged
dependencies, unchanged original services/firmware/bootstrap, real PCI/supplier
observation, preserved CLONE_NEWNET and no association/OOBE stop.
Three tests exercise the exact observation shell using temporary mock sysfs:
no PHY and an interface name alone both exhaust the bound with status 124;
a PHY symlink stops the poll, without asserting connectivity. Five independent
evidence-parser tests also pass, including duplicate snapshot deduplication and
firmware identity/error observations not being confused with target networking.

## Verified hardware progress

The final recovered cumulative phase is phase-070.log, SHA256
1d64e706aaa9fc2f1108d4dc01448a77717d1112b408f1cdd6b93b519ec82e46.
network-analysis.json classifies independent observations without inferring
network or desktop success. Relevant original records in that phase:

- All three module commands exit 0: pwrseq_qcom_wcn, pci_pwrctrl_pwrseq,
  ath11k_pci. The module inventory includes each.
- Lines 427/454/474 show original driver bindings for the Wi-Fi PCI endpoint,
  its PCI power-control platform device, and WCN6855 PMU respectively.
- At 6.153608 s, PCI 0006:01:00.0 enumerates endpoint [17cb:1103].
- At 6.192182 s, original ath11k identifies wcn6855 hw2.1.
- At 6.359369 s MHI requests power on; at 6.360380 s setup succeeds.
- At 6.446173 s MHI waits for SBL or Mission mode.

Compared with 079's early prefix without a Wi-Fi endpoint/hardware bind, adding
the authentic power dependencies advances the real hardware chain. This does
not prove the only remaining issue, a running WLAN firmware, or connectivity.

## Remaining boundary and next concrete dependency

The complete bounded early observation reports NETWORK080_POLLS=40 and exits
124: no PHY symlink appears in that window. No firmware version line is
recovered. The captured prefix has no ath11k error/crash line, but the final
kernel-log probe is budget-refused, so later behavior is not established by
absence from the early prefix. Target timeout and target exit status 9 are
recovered; no association or namespace migration was requested.

Read-only local kernel source provides the next specific dependency:

- drivers/net/wireless/ath/ath11k/mhi.c defines IPCR channels.
- net/qrtr/mhi.c binds the IPCR MHI channel and registers its QRTR endpoint.
- ath11k/qmi.c:3168 connects the new firmware service using AF_QIPCRTR and
  schedules the original SERVER_ARRIVE event.
- ath11k/qmi.c:2200 onward requests target capabilities; its original firmware
  version print is at line 2281 after reading that QMI response.

080's recovered module inventory includes qrtr but not qrtr_mhi. The earlier
working-Ubuntu lsmod includes qrtr_mhi. The base archive already includes
net/qrtr/qrtr-mhi.ko (read-only 079 archive audit). The custom outer starter
does not implement Ubuntu's general hotplug module-loader path. A next bounded
candidate should explicitly load this original transport module, rather than
fabricating firmware identity, extending waits without evidence, or changing
QMI/authentication behavior. Also capture MHI device/driver and original kernel
state so a missing transport can be distinguished from firmware boot failure.

Even after a genuine outer PHY appears, CLONE_NEWNET keeps the target separate;
standard privileged namespace transfer and genuine supplicant/NetManager
integration are still required. Ubuntu has original /usr/sbin/iw and
/usr/sbin/wpa_supplicant available; no executable/dependency copies or network
credential reads were performed in this turn.

## Recovery and preservation

All 80 recovered evidence files match their remote hashes. Recovery did not
replay the original LAB partition journal. Post-return verification passes
Ubuntu current/persistent default, firmware, all four original image hashes,
enabled/active screen-off timer, unmounted LAB and original manual entry.
141 baseline EFI files are unchanged except normal loader/random-seed and
hash-archived user-authorized removal of entry 078. Experimental entry files
retained: 079/080. Retention stamp: 20261115T035504758713Z. Shared payloads remain.
ESP free after install: 38,776,832 bytes; the 32 MiB headroom guard is unchanged.

No original activation/provisioning record, security check, package signature,
original service definition or OOBE lifecycle callback was changed. Do not
rerun completed operational 080 or claim desktop success from these findings.
