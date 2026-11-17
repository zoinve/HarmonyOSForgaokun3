# Native Wi-Fi kernel bring-up 079

Purpose: remove the verified missing WCN6855 firmware input and explicitly load
the already-present ath11k_pci driver, observing genuine kernel readiness.
This is a prerequisite diagnostic, not a claim that OOBE or the desktop works.

Read-only 079 archive audit matched all ten 078 deployed initrds by SHA256.
ATH11K, ATH11K_PCI, CFG80211 and MAC80211 are configured as modules; modules
and dependencies are packaged. No ath11k firmware is packaged and the outer
starter does not explicitly load ath11k. Source Ubuntu sysfs/dmesg confirms
PCI 17cb:1103 subsystem 17cb:0108, WCN6855 hw2.1, using ath11k_pci.

The existing Ubuntu firmware was copied read-only to a fresh WSL directory.
The candidate includes original main hw2.0 firmware/notice, original hw2.1
symlink, and original regulatory database/signature. Optional nfa765 alternate
firmware is not selected. All copied file hashes must match the source
manifest. No download, firmware modification, regulatory override or signature
exception is introduced.

Outer init adds one 15-second bounded modprobe after graphics enumeration,
followed by an 8-second bounded read-only kernel/netif observation. It then
continues unchanged original HarmonyOS initialization. Firmware failure is
recorded and does not count as readiness. A modprobe timeout does not prove
that uninterruptible kernel work was reaped; original outer return bounds and
logging remain active.

The own diagnostic init service now only reads /proc/net/dev and /proc/net/route.
It no longer starts or stops the guide and sends no finish events. All original
service definitions and the original bootstrap are byte-preserved. No Wi-Fi
credentials are read, no association/scan is commanded, no NetworkManager
connected state is synthesized, and no activation/provisioning record changes.

Keep the original 270-second outer and 150-second target limits, Ubuntu current
and persistent default, screen-off timer enabled/active, original images and
manual entry. Install requires the existing 32 MiB ESP headroom beyond the new
overlay. The package limit grows from 2 MiB to 8 MiB to accommodate authentic
firmware; the installation space guard remains unchanged. Retain only 078/079
entry files after hash-archiving 077; keep all shared payloads intact.

Evidence gates: exact archive delta, copied firmware hashes, unchanged original
services/bootstrap, one bounded driver load, no OOBE stop, one numbered boot,
read-only evidence recovery and full return-preservation verification.
Kernel firmware identity and a real wireless netif would establish kernel
bring-up only. Actual association, IP/DNS/routes, original NetManager admission,
normal OOBE completion and visible desktop interaction remain separate gates.
