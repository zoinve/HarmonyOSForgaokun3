# Genuine hardware identity path, read-only audit 091

No operational entry 091 has been installed or booted. No serial parameter,
UDID, activation/provisioning record, token or original binary was modified.

## Error classification and runtime evidence

Pinned official OpenHarmony 6.0 SoftBus header maps -426049513 to
SOFTBUS_NETWORK_GET_LOCAL_NODE_INFO_ERR. It is not by itself proof of a denied
authentication permission. The device-manager client uses a generic
CheckAuthentication failure message when its response error is nonzero.
Pinned source bytes, hashes and provenance are in
`original-udid-inputs-audit-091/result.json`. This public-source mapping is not
claimed to prove the private commercial binary is otherwise identical.

Original 089 native evidence independently shows SoftBus GetCommonDevInfo logging
GetDevUdid failed, LnnFirstGetUdid failing COMM_DEVICE_KEY_UDID, empty local UDID,
and device_manager GetNodeKeyInfo returning this same error. The original
collaboration service then spends 15125 ms completing its first filter request,
versus 17 ms after SceneBoard restarts. These observations identify an important
missing prerequisite, but do not yet prove the local UDID is the sole owner of
the observed service-side wait.

## Original module and reference behavior

The image's `/system/lib64/init/libudidmodule.z.so` is 8984 bytes, SHA256
`322f5cf59d309e4306e59bf47c11e01748c26d1039492c6e05e9afebe8f9e11c`.
Read-only symbol/string inspection confirms SystemReadParam/SystemWriteParam,
ohos.boot.sn, const.product.manufacturer/model/udid/devUdid and matching original
calculation-failure messages. It was extracted for inspection, not executed.

Pinned startup_init source reads ohos.boot.sn for the serial. The original
UDID module first checks existing original UDID parameters, otherwise combines
manufacturer/model/serial and calculates the hash itself. GetDevUdid reads the
resulting original parameters. Do not replace it with a fabricated success API
or implement a substitute identity algorithm.

HarmonyMac `ports/tools/adapt-local-root.py` explicitly retains the original
libudidmodule.z.so; its VM launcher supplies the VM's disk serial as boot.sn.
Its read-only `ports/tests/device-identity-probe.c` reports parameter/API return
codes, lengths and serial-source equality without printing identity values.
The virtual-identity/disk-fixture policy must NOT be copied onto this physical
MateBook. The pinned L410 trees do not supply an alternative matching UDID
implementation in the searched native sources; keep their actual service and
namespace integration, not invented identity values.

## Real physical source

Read-only Ubuntu firmware audit `native-hardware-serial-audit-091/result.json`
finds a printable nonplaceholder 16-byte DMI product serial whose hash matches
the chassis serial. Board serial is a distinct 16-byte value. A SoC serial also
exists; it is not interchangeable with the product serial. Only metadata,
lengths and hashes were exported, never the serial values. No hardware or
parameter writes were performed.

Existing experiment kernel options contain no ohos.boot.sn. This alone does
not prove the live parameter is absent: another original provider might supply
it. Before a hardware-supply change, query the original parameter/GetDevUdid
APIs without exporting values and verify the original module's availability in
the running namespace. Any repair must use the actual physical firmware source,
retain an existing valid identity, refuse conflicting values, and let original
policy/API/module code accept or reject the data. No arbitrary UDID, other
device's serial, virtual-identity flag, token forgery or activation-state edit.

## Current result

090 already demonstrates real WPA disconnect/reconnect, original validated
capability callbacks to the same guide process, and complete full-resolution
frames. OCR recognizes an activation-in-progress message, not success. The
native interactive desktop objective remains incomplete. Preserve 090 evidence
and Ubuntu before the next bounded integration attempt; do not repeat a
force-stop-only boot or claim normal Internet reachability completes OOBE.
