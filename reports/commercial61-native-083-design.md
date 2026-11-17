# Commercial Native 083 Design

082 proved genuine wlan0 visibility in the target network namespace. 083 runs
Ubuntu's original wpa_supplicant2.11/nl80211 and wpa_cli with hash-pinned original
dependencies, a blank network configuration, and the existing original bridge's
control path `/data/local/tmp/wpa_ctrl/wlan0`. No saved Wi-Fi credentials are read
or supplied, no association is requested, and OOBE/security/provisioning state is
not changed. This experiment verifies real control and scanning, not activation.

## Package And Isolation

The tools package is 7,579,585 bytes, SHA256
`3c86d698ad5ef83a3664d64d9041b760c99feaac17e6710d0ee9eb20ddaca91a`.
It is stored in a new user-owned Ubuntu lab directory, not the ESP. The existing
diagnostic read-only/noload Ubuntu mount exposes the file. A twelve-second bounded
operation verifies the embedded expected hash before extracting the deterministic
regular-file/directory-only archive into target RAM. Existing original images and
bootstrap/service configurations are unchanged. Package members were independently
verified against the original tool capture manifest. The archive has no credentials.

The helper opens the exact target root and net/mnt/pid namespace descriptors before
joining, requires each namespace differ from the caller, then joins with normal
kernel capability checks. A fork enters the selected PID namespace; the worker
chroots to the held target root and verifies root and all three namespace identities
before exec. The real daemon is thus cleaned up when target PID1 exits. No namespace
is removed, no original process identity is impersonated, and no checks are patched.

## Runtime Procedure

After the existing original iw migration, sample2 invokes start once with a ten-
second budget. It requires original RAM-ext4 /data and the target temporary parent,
and creates only the dedicated control directory root:wifi(1010), mode0770.
The verified original wifi UID/GID is1010. Configuration contains ctrl_interface,
update_config=0 and ap_scan=1 only, without network blocks. The original service
retains its existing wifi identity and permissions.

Only after start exits zero, five-second bounded CLI probes request ping and one
scan. At sample4, bounded queries request scan_results and status, followed by a
read-only dump of at most64KiB of the real daemon's log. No keys-debug flag is used.
A CLI process exit zero is not enough: evidence must contain PONG, scan OK, and
actual BSS rows under the verified target context to establish these operations.
Even real BSS results are not proof of association, IP, DNS, NetManager or OOBE.

The 270-second outer return, original image/default boot preservation, active
screen-off timer, 32MiB ESP headroom guard and two-entry retention remain mandatory.
