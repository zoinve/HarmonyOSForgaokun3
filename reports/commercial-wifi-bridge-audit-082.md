# Existing Wi-Fi Bridge Audit 082

Read-only evidence is under `commercial-network-source-audit-082/result.json`.
The source image was opened only through debugfs without write mode; no extracted
private binary was executed or patched.

The existing `wifi_standard.cfg` starts `sa_main` with
`/system/profile/zz_l410_wifi_bridge.json`, UID wifi, original supplementary groups,
CAP_NET_ADMIN/NET_BIND_SERVICE/NET_RAW, and its existing CONNECTIVITY_INTERNAL,
NETWORK_DHCP, GET_NETWORK_INFO and Wi-Fi permissions. No permission additions or
identity substitution are required by this finding. Config SHA256:
`52d543be69ef60f3165917fe3a10c405f4bb2d39d4693938a31b6994c94e0480`.

The profile loads `/system/lib64/libl410_wifi_compat_v20.z.so` for SA1120, 1121,
1123 and 1124, with original DHCP client/server SAs1126/1127. Library SHA256:
`e795c7a4c336b9eacd9ad241886044d04ef74baac6ebe6e74740c5fb128ddba8`.
Its ELF SONAME is libl410_wifi_compat_v18.z.so; do not infer version equivalence
from either filename. The binary contains the control path
`/data/local/tmp/wpa_ctrl/wlan0`, `/proc/net/route`, `/system/bin/ip`, and an imported
NetConnClient::RegisterNetSupplier symbol. Dynamic dependencies include the
original IPC, SA, NetConn and DHCP libraries.

081 runtime hilog records the bridge process starting and loading its DHCP client
service. This is not proof its Wi-Fi SAs completed registration or that a supplier
was published. Actual supplicant communication and real network validation remain
unproven.

The pinned L410 reference's v2 source reads real interface addresses, routes and
WPA status before publishing a supplier; later wrapper versions extend that base.
It also contains legacy placeholder branches. Do not import those placeholders,
assume private ABI compatibility, or synthesize connected/provisioned state.
HarmonyMac's force-stop cannot complete OOBE because the existing SceneBoard
recovery path restarts it, as independently proven in 078.

Next integration should first verify 082 target-netns interface visibility, then
place a genuine supplicant control socket at the existing bridge path, verify real
scan/association/IP/route/DNS state, and observe original NetManager/OOBE behavior.
The supplicant must share the target network namespace and a consistent filesystem
view of the server UNIX socket. The pinned reference's WpaRequestAt uses an abstract
client socket named `l410_wifi_%d_%u`, not a target-local pathname client socket.
Both this format string and the server pathname occur in the extracted original
binary. Abstract socket lookup depends on network namespace identity; an outer-only
server pathname alias does not establish that identity or prove reply routing.

The reference's MonitorWifiState requires both completed WPA status and CarrierUp
before emitting connected state, then starts real DHCP/static provisioning. Its
DHCP path consumes actual client callbacks or the stock client's real cache and
publishes the resulting address/routes/DNS. These are source-level integration
entry points, not proof that the provided private binary is ABI-identical or that
any live supplier registration has succeeded on this machine.
