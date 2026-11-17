# Native Wi-Fi bring-up 079 outcome

One completed operational boot, 2026-11-15 03:39:26 to 03:43:08 UTC:
commercial61-native-079-bac2b37a-f7e6-4fdf-af2d-25845772face.
Returned Ubuntu boot ID 341ed244-b5ba-465e-a35f-fad64ebc534f.
The desktop objective remains incomplete; no OOBE/activation/network success.

## Changes and admission

The 3,644,008-byte exact incremental overlay SHA256 is
2402130b010ff40232102f5fc8d700ca31184ad84f61a6e53b0372f0239b7571.
The full candidate preserves the 078 original bootstrap byte-for-byte:
c136b0522ea34a167f372fd5df35b31b38cc0b26ce512e6c1b561aca67004dd7.
Changes are outer init, the own diagnostic script/config, and original WCN6855
firmware/regulatory files plus their directory/symlink records. No original
service definition, source image, HAP, authentication check or activation state
is changed. This candidate does not call aa start/force-stop or finish events.

The existing Ubuntu working firmware was read-only copied and hash-verified.
Observed source PCI identity is 17cb:1103 subsystem 17cb:0108; original Ubuntu
dmesg explicitly identifies WCN6855 hw2.1 and its running firmware version.
The source firmware-stage manifest includes hashes and the original hw2.1 to
hw2.0 symlink. No credentials or host network configuration were read/changed.

Exact archive delta, original-service preservation, original-bootstrap identity,
copied firmware hashes, bounded probes and no-association/no-OOBE-stop admission
checks pass. Six archive parser rejection/round-trip tests and five conservative
network-evidence tests pass. The seven preceding OOBE decoder tests also pass.

## Actual kernel result, not a successful Wi-Fi claim

Recovered phase-066.log is a cumulative snapshot. Relevant original lines:

- 314-316: wifi-driver079 begins and exits status 0.
- 326-333: ath11k_pci, ath11k, mac80211, cfg80211, rfkill, MHI and QMI modules
  are present in /proc/modules.
- 320-365: immediate netif inspection shows only lo; no wireless interface.
- The captured kernel prefix contains cfg80211 certificate initialization,
  but no ath11k firmware version or hardware-bind record.
- 280081-280082: target timeout and target exit status 9 are recovered.
- The final kernel-log probe was budget-refused, so no final dmesg proves that
  no delayed bind happened later. Absence of an early record is not proof of
  absence throughout the whole runtime.

network-analysis-revision2.json selects the final cumulative phase only,
SHA256 729aa6c72c44a3f0cd927a5a60df55d19b5b322bd5acf5adfed5357e157f1420.
The initial network-analysis.json is preserved: its duplicate status records
come from concatenated cumulative snapshots, not repeated modprobe calls.

Conclusion: original module load is proven, physical Wi-Fi readiness is not.
No association was requested, no address was obtained, no HarmonyOS default
network was established, and no normal OOBE completion/desktop action is proven.

## Next dependency and namespace boundary

The diagnostic kernel configuration also has
CONFIG_POWER_SEQUENCING_QCOM_WCN=m and CONFIG_PCI_PWRCTRL_PWRSEQ=m.
Current outer init does not explicitly load pwrseq_qcom_wcn or
pci_pwrctrl_pwrseq. Read-only post-return Ubuntu lsmod shows both are loaded
in the working system. Kernel board DTS describes a WCN6855 PMU, enabled PCIe4
and the Wi-Fi endpoint's PMU regulator supplies. This identifies a concrete
missing startup dependency to test; it does not yet establish the sole cause.
079 did not capture a full PCI/supplier sysfs inventory for that endpoint.

The existing native_child clone also includes CLONE_NEWNET. Even if the outer
netif appears, the original target cannot automatically use that interface.
The same local kernel nl80211_wiphy_netns supports original namespace migration
by PID or namespace FD, requiring CAP_NET_ADMIN over source and target. Preserve
these checks and the namespace; do not replace them with a fake connected state.

Next bounded candidate should load original board power dependencies before
ath11k, capture PCI/supplier and phy/netif state over a bounded observation
window, and only then address transfer to the genuine target namespace and
supplicant/NetManager integration. Do not rerun completed 079 or repeat OOBE
kills. Known original Settings/AppGallery source-package defects remain separate
dependencies and must not be worked around by signature or package-state forgery.

## Recovery and preservation

All 76 recovered file hashes match; original LAB partition journal was not
replayed. Verification passes Ubuntu current/persistent default, firmware,
all four original image hashes, enabled/active screen-off timer, unmounted LAB
and original manual entry. 140 baseline EFI files are unchanged except normal
loader/random-seed and the user-authorized hash-archived removal of 077 entry.
Entry files retained: 078/079; shared kernel/initrd/image payloads remain intact.
Retention archive stamp: 20261115T033914776306Z. ESP free after install was
39,137,280 bytes; the 32 MiB installation headroom guard was not weakened.
