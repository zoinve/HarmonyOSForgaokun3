# Commercial Native 083 Closure

## Result

Genuine supplicant control and real wireless scanning succeeded in the target
context. The hash-pinned tools archive was verified and extracted into RAM. All
six bounded start/ping/scan/scan_results/status/log phases exited zero. Each helper
verified target PID405, net namespace inode4026532976, mount namespace
inode4026533019, PID namespace inode4026532975, and the exact target root.

The original wpa_supplicant2.11 started with nl80211 and the credential-free
configuration. Original wpa_cli returned PONG, scan returned OK, and scan_results
contained four actual BSS rows. The report records hashes of those rows rather
than copying surrounding SSIDs. Original status was INACTIVE, not connected;
the daemon log recorded real driver regulatory events for CN. No connection
credentials were read or supplied, and no association was requested.

This proves target supplicant control and real RF scanning, not IP/DNS,
NetManager default-network admission, OOBE completion, or native desktop behavior.
The original Wi-Fi bridge's direct use of the control interface is still unproven.

## Evidence And Tests

Run `commercial61-native-083-3ea78423-9ade-41f5-a871-387bb4bca3ad` started at
2026-11-15T04:42:25.343213Z and returned at 2026-11-15T04:46:08.543000Z. It ran once;
the bounded target timeout ended PID405 with status9. All100 retrieved evidence
files matched remote hashes.

Cumulative `runtime-evidence/raw/phase-090.log` SHA256:
`dca95948634f04d28afd18545887dd1d5772f526aa7a5ad09aaa78b4e3c67958`.
Lines43327-43338 contain the real start/PONG/scan responses. Lines79995-80011
contain INACTIVE status and the original daemon log. See network-analysis.json
for the verified contexts and hashed scan rows.

Exact archive admission passed: only init changed among existing members;
new files were the isolated static helper and blank target config/directory.
Bootstrap, original services/configuration and firmware were unchanged. Seven
exact-command tests passed; six analysis tests passed after fixing an invalid
numeric regex backreference before the operational run. Cross compilation used
-Wall -Wextra -Werror. None of these tests substitutes for runtime evidence.

## Preservation

Overlay661,534 bytes, SHA256
`5948ffcb6b6f45121eb05e20b04d8fe1ac4bd89cd8104156d52f8e1f4cd6e091`.
ESP free35,995,648 bytes after installation; the32MiB guard was retained. The
7,579,585-byte original tools package lives outside the ESP in a new lab input
directory, with SHA256
`3c86d698ad5ef83a3664d64d9041b760c99feaac17e6710d0ee9eb20ddaca91a`.
It contains no credentials. Historical shared boot payloads were not removed.
Retention stamp20261115T044147064753Z archived/removed only081 entry;082/083 remain.

Ubuntu returned with boot ID07c634ce-8a9f-46f3-a19c-5f075804783b and remained current
and default. Verification confirmed144 prior EFI files unchanged, boot-managed
random seed excepted, the authorized archived081 entry removal, unchanged
firmware and four original images, unmounted lab partition, active/enabled
screen-off timer and the original manual entry.

## Next Boundary

Use the existing real wireless network, with credentials kept out of repository,
logs and initrd, to verify association. Then observe the unchanged original
bridge's real DHCP and NetManager publication, independently checking actual
addresses/routes/DNS before revisiting original OOBE. Do not synthesize connected
or provisioned state, impersonate a service, or repeat OOBE kills. The complete
native desktop goal remains active and unachieved.
