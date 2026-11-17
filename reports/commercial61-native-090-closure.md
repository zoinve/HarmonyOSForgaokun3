# Experiment 090 closure

Exactly one entry-090 boot, 2026-11-15 07:18:16.844075 to 07:22:00.708049 UTC.
Inherited-core raw run: `commercial61-native-087-939b8e48-cd41-4991-a1be-dc1c8dfd844b`.
All 131 files matched remote sizes/hashes; no historical run was overwritten.

## Native network transition

One original wpa_cli disconnect and one reconnect were requested, both reporting
OK/exit 0. More importantly, actual WPA status changed COMPLETED -> DISCONNECTED
-> COMPLETED. Original bridge DHCP completed again at 15:20:42.245 local time;
the same guide PID 6252 received capability list 12,15,16 at 15:20:42.040. The
guide had already reinitialized networking and received 16 at 15:20:02.281, so
the final successful callback must not be presented as the first validation or
as independent proof that the reconnect alone fixed every callback problem.

No guide stop, fake network event, certificate bypass or credential change.
Independent original HTTP/HTTPS probes returned 204/exit 0, HTTPS verification 0.
Credential secrecy comparison passed across all retrieved files.

## Desktop and OOBE

One original SceneBoard PID 4608 registered a root scene. It completed Dock at
15:19:47.766 and its slow original collaboration query recovered at 15:19:55.690.
No thread-freeze capture was returned in this run; absence of a capture alone
is not a guarantee of zero stalls. PID 4608 and guide PID 6252 survived at uptime
120/135. No native desktop or completed OOBE is claimed.

Both 2560x1600 source captures are complete, with lossless rotated output.
Local source-image OCR at uptime 120 reads a message that activation is underway
and that Huawei collects device identifiers for activation/rights information.
OCR is not direct visual inspection or desktop interaction proof. No fake
activation state was introduced. The screen is no longer adequately described
as merely lacking a network: actual validated networking is demonstrated.

## Next evidence and safeguards

Read-only comparison of 088/089 collaboration logs is under
`commercial-collaboration-latency-audit-090`: first query 9577 ms in 088; first
15125 ms and later 17 ms in 089. Original SoftBus additionally reports
GetDevUdid failed and an empty local UDID. The numeric error -426049513 should
be mapped against pinned primary source, not treated as proof of a denied
permission merely because its caller labels the failure CheckAuthentication.

Read-only Ubuntu hardware audit 091 finds a real 16-byte DMI product serial,
matching the chassis serial hash, plus a distinct board serial. Only lengths,
hashes and source metadata were exported. No identity/provisioning changes.
Investigate the original UDID input/module path and real hardware data supply;
never invent a UDID, copy another device's identity, or patch verification.

Eight shell-flow scenarios and exact one-text-member archive admission pass.
Serial post-retrieval preservation passes Ubuntu current/default, 151 baseline
EFI files, firmware/four original image hashes, unmounted lab, screen-off timer
enabled/active, manual entry and shared payloads. Only authorized archived entry
088 was removed; retained experiment entries are 089/090. Goal remains active.
