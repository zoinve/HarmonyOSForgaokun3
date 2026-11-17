# Commercial Native 084 Closure

## Real Networking Progress

Actual WPA2-PSK association completed. Original supplicant status progressed from
SCANNING to COMPLETED. Kernel getifaddrs reported wlan0 IPv4 192.168.10.124/24 and
an IPv6 link-local address. The real default route points to192.168.10.37, matching
the stock DHCP cache's router and DNS1; its DHCP server is192.168.10.1. The helper
did not install an address or route and did not replace the original DHCP service.

Original hilog independently proves the full service handoff:

- At early uptime29.436, the existing bridge's DhcpClientServiceImpl reported real
  IPv4 success for wlan0.
- At30.308, original NetManager registered wlan0 supplier1003, netId100.
- At31.576, original NetManager selected supplier1003 as default; link update
  completed at31.582.
- Original NetManager subsequently reported multiple HTTPS detection successes.
- Original OOBE reported hasDefaultNet:true in all three observed guide processes;
  the first also logged network availability and capabilities12,15,16.

The expected optional bridge status files were absent. The phase-only analysis
therefore conservatively did not prove publication. This was not a publication
failure: `native-service-network-analysis.json` supplements that untouched report
with actual DHCP/NetManager/OOBE records. Original HTTPS success is still a service
report, not an independent original-curl DNS/TLS verification.

## Remaining Desktop Blockers

OOBE did not finish. Guide PIDs6213,9121,11968 and SceneBoard PIDs4323,8361,10040
were observed across restarts. The latter guide processes still logged an eight-
second network-validation wait timeout despite hasDefaultNet:true. Do not equate
working kernel Wi-Fi/default-network visibility with successful guide completion.
No stop loop, forged completion record, service impersonation, private binary
patch, or disabled lifecycle/security check was introduced.

Next independently verify original curl against the original probe configuration,
then distinguish OOBE validation callback behavior from SceneBoard restart causes.
Real native desktop pixels and visible interaction remain unproven.

## Evidence And Preservation

Run `commercial61-native-084-a7892483-9c37-42f0-b088-0b7909dfe7d1` ran once,
2026-11-15T04:57:35.693470Z to2026-11-15T05:01:22.459875Z. Early Jan1 hilog labels
precede the original time service's network time synchronization; these are not
separate historical boots. The bounded target timeout ended PID409 with status9.
All120 retrieved files matched remote hashes.

Cumulative phase110 SHA256:
`f7cdeb7c3bf987f1316c0654c6f558524226aec019c4175239657a32ec430729`.
Original interactive hilog SHA256:
`628bb20c202a323367a800ef54e8730abdec9440d4b0c3beae4c46cc7aadcf38`.

Exact archive admission passed: only init changed among existing members, and
the two additions were the static helper and private RAM directory. No credential
was packaged or exported. The private config was generated on-device from the
active legitimate Ubuntu connection, protected0400 inside0700, hash-verified and
copied only to target RAM. Original Ubuntu networking was not modified.
An on-device digest comparison against all120 retrieved files (382,750,988 bytes),
including overlapping hexadecimal windows, found no occurrence of the private
64-hex PSK value. Only candidate digests and a match boolean crossed the transport;
the original audit and strengthened revision2 evidence were both preserved.

Seven exact-command tests, seven exact read-only observer tests, six phase parser
tests and five native-service correlation tests passed. Cross compilation used
-Wall -Wextra -Werror. Original bootstrap/services/firmware remained unchanged.

Overlay667,705 bytes, SHA256
`d836343a012d9a7376e22d3bac959eabeb117711535a9750f350ea84851c8ef7`.
ESP free35,319,808 bytes after install, with32MiB guard retained. Retention stamp
20261115T045726253057Z archived/removed only082 entry;083/084 and all shared
payloads remain. Ubuntu returned with boot ID80d56a76-a510-4f9f-aff2-2cb1b683c55a.
Verification confirmed Ubuntu current/default,145 prior EFI files unchanged
(boot-managed random seed excepted), authorized archived082 entry removal,
unchanged firmware and four images, unmounted lab partition, enabled/active
screen-off timer and original manual entry.

The original probe config/curl identity was read-only audited separately under
`commercial-network-probes-audit-084`. No probe request was sent by that audit.
