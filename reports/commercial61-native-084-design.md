# Commercial Native 084 Design

083 proved real supplicant control and four BSS results in the exact target
net/mnt/pid namespaces. 084 requests genuine association using the same currently
active Ubuntu Wi-Fi connection. Existing DHCP, Wi-Fi bridge, NetManager, OOBE and
all original service identities/configurations remain unchanged.

## Credential Boundary

On the device only, nmcli reads the active profile and its saved WPA-PSK. The
passphrase is converted with standard WPA PBKDF2 when necessary; the existing PSK
is used directly otherwise. A config is created only in a new user-owned0700
experiment directory, mode0400, without changing Ubuntu's connection. Neither
SSID nor credential content is returned to the workspace. Only readiness,
permissions, size and SHA256 are recorded. No private config is in the initrd.

During diagnostic boot, the existing verified read-only/noload Ubuntu mount
exposes the file. An eight-second bounded operation compares its expected SHA256,
copies it into a0700 target RAM directory and sets0400 mode. No config content is
printed. Supplicant uses the existing isolated083 binaries and authentic tools
package; it is not built with keys-debug flags or configured to save changes.

## Association And Observation

The helper preserves083's exact-root and three-namespace verification, but starts
supplicant against the private084 RAM config. One automatic real WPA-PSK
association is requested. The earlier manual scan is replaced by status so it
does not interfere with association. No IP or route is installed by the helper.

At samples4/7/10/13, bounded observers report real getifaddrs addresses, proc IPv4/
IPv6 routes, carrier/operstate, and only these original bridge/DHCP state files:
netmanager-v4.status, natural-control-v6.status and dhcp_cache.conf. Reads are
limited to16KiB per file and64 interface records. Status and at most64KiB of the
original supplicant log are also captured. A failed start still gets a log read.
Credential files are never part of the observation allowlist.

Association requires original status COMPLETED. Original bridge-reported success
and actual kernel addresses/routes are separate evidence; neither proves DNS,
Internet reachability, default-network selection or OOBE completion by itself.
Do not synthesize supplier state, impersonate an original service, patch private
binaries, or repeat guide kills if the real networking path fails.

The bounded270-second return, active screen-off timer, immutable original images,
Ubuntu default boot, original manual entry,32MiB ESP reserve and hash-archived
two-entry retention remain required.
