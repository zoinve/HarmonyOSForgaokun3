# Native Wi-Fi power dependencies 080

Goal remains a real original HarmonyOS desktop with full-resolution pixels and
genuine visible interaction. This candidate tests the next concrete networking
prerequisite; it does not redefine desktop success as loading kernel modules.

079 proved ath11k modules load but its immediate observation saw only lo and
no firmware/hardware-bind record. Its final dmesg was budget-refused, so 080
adds a bounded early observation instead of claiming later absence.

Read-only source evidence: the kernel has
CONFIG_POWER_SEQUENCING_QCOM_WCN=m and CONFIG_PCI_PWRCTRL_PWRSEQ=m; both modules
are already in the hash-verified base archive. Local kernel
drivers/pci/pwrctrl/pci-pwrctrl-pwrseq.c matches pci17cb,1103, and
drivers/power/sequencing/pwrseq-qcom-wcn.c matches qcom,wcn6855-pmu.
The board DTS describes the PMU supplies and enabled Wi-Fi PCIe endpoint.
Working Ubuntu lsmod includes pwrseq_qcom_wcn and pci_pwrctrl_pwrseq, while
079's explicit starter and recovered module inventory lack them.

Exact candidate delta from 079: outer init only. Original bootstrap, services,
firmware, images, diagnostic observation script and 270/150-second return
bounds are unchanged. The inherited own service still has internal name
matebook_desktop079 and its harmless observation marker remains 079; it does
not start/stop OOBE or send completion events.

Load pwrseq_qcom_wcn (8-second command bound), pci_pwrctrl_pwrseq (8 seconds),
then ath11k_pci (15 seconds). Observe for up to 40 quarter-second polls for a
real /sys/class/net/*/phy80211 symlink, within a 15-second command bound.
Collect PCI/platform driver links, device IDs, supplier links, available
deferred-device records, modules, interfaces and an early dmesg. If no PHY is
observed, the observation exits 124 without asserting connectivity; normal
original HarmonyOS boot continues. Command exit zero alone is not readiness.

No Wi-Fi credentials, scan or association, address fabrication, NetManager
availability forgery, activation-record edits or signature exceptions. Original
CLONE_NEWNET remains in place. No namespace migration is attempted in 080.
Even a real outer PHY is not a target default network, OOBE completion or a
usable desktop. These remain separate required integration gates.

Preflight requires exact init-only archive delta, packaged dependencies,
bounded ordered probes, unchanged original services/firmware/bootstrap and
unchanged namespace. Install preserves the existing 32 MiB ESP headroom guard,
Ubuntu current/default and enabled/active screen-off timer. Retention must
hash-archive/remove only the 078 entry, keeping 079/080 and all shared payloads.
Execute one operational 080 boot only; recover evidence read-only and verify
all original images, firmware, EFI baseline and default boot after return.
