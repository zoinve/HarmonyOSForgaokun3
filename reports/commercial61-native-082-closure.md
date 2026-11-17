# Commercial Native 082 Closure

## Result

Real wireless PHY migration succeeded without removing CLONE_NEWNET. The original
iw move exited zero. The observer opened PID394's network namespace, required a
different identity, joined it and verified inode 4026532976 (source 4026531833).
Original iw dev then listed phy#0 and wlan0, ifindex2, type managed, before exiting
zero. A subsequent outer observation listed only lo.

This proves target-network-namespace wireless visibility, not association, address
assignment, Internet connectivity, NetManager publication, OOBE completion or
desktop interaction. No association, credentials, OOBE stop or activation-state
change was requested. Original service configurations and bootstrap were unchanged.

## Evidence

Run `commercial61-native-082-8991b382-2007-4588-b69a-801ee086045d` started at
2026-11-15T04:23:54.437222Z and returned at 2026-11-15T04:27:39.316560Z. It ran once;
the bounded target timeout ended PID394 with status9. All 86 retrieved files
matched their remote hashes.

Cumulative `runtime-evidence/raw/phase-076.log` SHA256:
`fb484c49afa68e2f9a03d9562bbbc538bdd0400d0b23ec7cc8ce9fd755681c32`.
Lines1256-1278 preserve move status, target namespace identity and actual iw output;
line1280 records outer lo. See `commercial61-native-082/network-analysis.json`.

Exact archive-difference admission passed. Existing members changed only at init;
new regular files were exclusively isolated hash-pinned network tools and helper.
Six exact-helper mocked syscall tests and five evidence-parser tests passed.
Cross compilation used -Wall -Wextra -Werror. These tests are not runtime network
or desktop proof.

Overlay 1,741,669 bytes, SHA256
`cbdb78df5a10641c0e68f17544dd1be6c7ae8d681a1688ece7c0ab3e4c067678`.
ESP free space after installation: 36,663,296 bytes, with the 32 MiB guard retained.
Entry retention stamp20261115T042346337983Z archived/removed only entry080;
081/082 and every shared payload remain.

## Preservation And Next Step

Ubuntu returned with boot ID18cb0f38-8415-4084-9aa3-16753267a426 and remained the
current/default entry. Verification confirmed 143 prior EFI files unchanged,
boot-managed random seed excepted, the authorized archived080 entry removal,
unchanged firmware and all four original images, unmounted lab partition,
enabled/active screen-off timer, and original manual entry retained.

The existing original Wi-Fi bridge and its original permissions/control socket
contract were independently audited in `commercial-wifi-bridge-audit-082.md`.
Next integrate genuine supplicant in the target network and filesystem views,
verify real scanning and association, then real addresses/routes/DNS and original
NetManager/OOBE behavior. The full native desktop goal remains unachieved.
