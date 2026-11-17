# Experiment 091 closure

Exactly one entry-091 boot, 2026-11-15 07:49:29.067771 to
07:53:11.007609 UTC. Inherited-core raw run:
`commercial61-native-087-07288f77-1ad4-48b8-9d7a-1001af81bfdf`.
All 131 retrieved files match remote sizes/hashes. Historical labels are retained.

## Original identity APIs

The original GetParameter API returns empty ohos.boot.sn, const.product.udid
and const.product.devUdid. Runtime manufacturer length is 6 and model length
is 9. Original GetDevUdid returns 106, with no valid UDID.

Actual kernel sysfs provides valid matching 16-character product/chassis serials.
Runtime manufacturer matches the real firmware vendor, but runtime model does
not match firmware product_name. The helper therefore takes decision 13 and
exits 13 with no write requested. It never calls SetParameter or loads the
original UDID module. No raw serial or UDID values were exported. This confirms
a runtime hardware-metadata mismatch, not successful identity or activation.
See hardware-runtime-analysis.json for original return codes and lengths.

## Networking and pixels

The existing bounded original WPA commands again observe COMPLETED ->
DISCONNECTED -> COMPLETED, with one disconnect and one reconnect, both exit 0.
Original guide PID 6682 receives real capability callbacks 12,15,16 before
and after the cycle. No guide force-stop or activation-state modification.

Both uptime-120 and uptime-140 source captures are complete 2560x1600 frames;
PNG export and clockwise output rotation are lossless. Source-image OCR reads
the device-identifier collection explanation for activation/rights information.
OCR is not direct visual verification, activation completion or interaction
proof. The original UI layout tool did not provide a successful layout result.
OOBE completion and a stable interactive desktop remain unproven.

HarmonyMac's release README describes original aa force-stop at 116 seconds
as a development shortcut, explicitly not commercial activation. Local 078
already records BaseOobeManager sessionExceptionCallback relaunching the guide.
Repeating only that stop is not a demonstrated persistent solution here.

## Preservation and next prerequisite

Retrieval completed before serial preservation verification. Ubuntu is current
and default with boot ID 6a0d2200-324b-4a04-95b6-f088a51ec378. All 152 baseline
EFI files are unchanged except the boot-managed random seed and the separately
archived, user-authorized removal of entry 089. Entries 090/091, original manual
entry and shared payloads remain. Firmware and all four original images match;
the lab partition is unmounted and the screen-off timer is enabled/active.
Credential evidence comparison passes across all 131 files.

The next prerequisite is a reviewed early-boot path from actual physical
firmware to volatile hardware parameters before original init consumes product
constants. Do not use the borrowed L410 model with the MateBook serial, invent
an identity, lower the ESP free-space guard, alter provisioning, or claim that
identity repair alone guarantees commercial activation. No 092 change or boot
has occurred. The desktop goal remains active.
