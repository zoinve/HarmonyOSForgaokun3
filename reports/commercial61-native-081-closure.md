# Commercial Native 081 Closure

## Result

The original WCN6855 hw2.1 firmware initialized successfully. The early observer
found `/sys/class/net/wlan0/phy80211` after two polls. Later observations retained
`wlan0` with `operstate=down` and a link to `phy0`. This proves driver and PHY
initialization, not association, Internet connectivity, OOBE completion, or desktop
interaction.

The IPCR MHI device bound to `qcom_mhi_qrtr`. The original kernel reported firmware
version `0x11088c35`, build timestamp `2024-04-17 08:34`, and build ID
`WLAN.HSP.1.1-03125-QCAHSPSWPL_V1_V2_SILICONZ_LITE-3.6510.41` at 7.390272 seconds.
All five bounded Wi-Fi setup/observation phases exited zero. No association or
network namespace migration was requested in this experiment.

Later bounded kmsg drains reported overruns; absence of selected errors cannot
establish absence of runtime errors. Original records and these limitations are
preserved in `commercial61-native-081/network-analysis.json`.

## Evidence And Return

Run: `commercial61-native-081-e4bd6bf8-0c0f-4cf7-aa72-bba71cfa4629`.
Started 2026-11-15T04:09:08.524512Z and returned to Ubuntu at
2026-11-15T04:12:51.827085Z. The bounded target run ended with status 9 after its
timeout. All 79 retrieved evidence files matched remote hashes.

Selected cumulative evidence: `runtime-evidence/raw/phase-072.log`, SHA256
`e08b0eb2b2eee5ff0f5c409aea70356a548a4e880fa90ca46e78156c45ca7608`.

Return verification confirmed Ubuntu current/default, no unauthorized prior EFI
changes (142 files unchanged; boot-managed random seed excepted), unchanged
firmware and four original commercial images, unmounted lab partition, original
manual entry retained, and screen-off timer enabled/active. The archived 079
experimental entry was removed under the user's two-entry retention requirement.

## Next Boundary

Keep `CLONE_NEWNET` and original permission checks. Use the existing original
`iw` implementation to move the PHY to the target namespace, then independently
verify interface visibility and real wireless behavior before claiming networking.
Read-only inspection of Ubuntu's `iw`, `wpa_supplicant`, and `ip` identified their
dynamic dependencies; no connection credentials were read or changed. HarmonyMac's
force-stop remains insufficient because SceneBoard restarts OOBE. No kill loop,
forged provisioning state, or activation bypass was introduced.
