# Experiment 092 closure

Exactly one entry-092 boot, 2026-11-15 08:10:32.559867 to
08:14:14.470396 UTC. Raw inherited-core run:
`commercial61-native-087-10b7b88c-1c9a-4d06-8e59-0e7331d6096a`.
All 131 retrieved files match remote sizes/hashes. Native timeout and target
exit status 9 are recovered. No numbered operational boot was repeated.

## Actual hardware-input progress

The new early entry verifies the unchanged outer init and original RAM
parameter hashes, mounts genuine sysfs, checks the physical MateBook board,
and changes only the RAM model input from actual DMI. Original images and
both existing startup cores remain byte-identical. Early result and temporary
sysfs unmount both return 0. The wrapper reads no serial or UDID.

At uptime 100 the original GetParameter API now returns a six-character model
matching genuine firmware, rather than the previous conflicting nine-character
model. Manufacturer also matches. Existing boot serial/UDID fields are empty;
original GetDevUdid returns 106. The unchanged 091 gate therefore chooses action
2. Original public SetParameter accepts the actual matching product/chassis
serial with return 0; original GetParameter reads it back matching firmware.
No arbitrary serial, synthetic model, substitute hash or provisioning state.

The subsequent original libudidmodule dlopen fails. Helper exit is 68, not
success; no after-phase valid UDID is established. Exact dlerror was not logged
by inherited 091, so do not assert an independently observed linker error.
All parameter changes are in this ephemeral target, not Ubuntu or images.

## Why the next step must use original init

Read-only ELF audit `original-udid-loader-audit-093-r2/result.json` shows the
original module imports SystemWriteParam; original init exports it, while the
original begetutil client does not. Original libinit_module_engine.so points to
the image's original empty stub and does not export that server API either.
mbedtls lives in chipset-sdk; sec_shared resolves to chipset-sdk-sp. Do not
invent a SystemWriteParam shim, replace the original stub, or load another
device identity to make a diagnostic dlopen appear successful.

Pinned upstream udid_static.c installs the original module from the pre-config
hook. The inspected standard init source loads product parameter files before
that hook. This supports supplying genuine boot inputs before original init
consumes them, rather than calculating UDID in a client process. Public source
ordering is not proof of every detail of the private commercial binary.
The first audit's absent top-level mbedtls-path failure remains preserved in
`original-udid-loader-audit-093`; revision 2 uses actual original paths.

## Desktop and network evidence

Native networking remains real: WPA COMPLETED -> DISCONNECTED -> COMPLETED,
one disconnect and reconnect, original guide capability callbacks 12,15,16,
and original curl HTTP/HTTPS 204 with HTTPS verification 0. This does not prove
activation or successful vendor attestation.

Two complete 2560x1600 source captures and their lossless rotated output were
exported. Source OCR recognizes no text in this run; this is not absence of
OOBE or proof of a desktop. Direct image inspection is unavailable because the
image tool rejects image inputs. The original UI layout tool provides no
successful layout evidence. No desktop or interaction success is claimed.

A complete 211270-byte original THREAD_BLOCK_3S event capture for SceneBoard
PID 4303 is recovered, hash c7c693761a2167eb869900d691ff1f4599a7b962b98a2f850ab5eff930b7a766.
Its main-thread stack is condition_variable wait -> assoc_sub_state wait ->
libcollabfwk_devicedetect_client -> libcfwk_devicepicker_client ->
Js_GetTrustedDeviceListSync. This establishes a real remaining main-thread
stall, not that missing identity is its independently proven sole cause.
The generic probes analyzer's empty legacy freeze list does not override this
complete capture from the artifacts analyzer.

## Tests, privacy and preservation

Sixteen archive/security admission checks and eleven synthetic fixture cases
pass using the exact target AArch64 BusyBox under qemu-user. Only filesystem
magic is simulated in fixture cases; these are not native runtime proof.
The first harness attempt used a non-BusyBox basename and failed applet
dispatch; the harness was corrected before installation. No native boot retry.
Incremental overlay is 2558 bytes, SHA256
967782bd489bd8c26b26cbf2fc27e7f95bc35d935f057a7a653b6cdf77d31c59.

Retrieval first performs an on-device physical-serial byte scan and passes
without exporting raw serial values; original evidence hashes are preserved.
Credential comparison also passes across all 131 files. Retrieval finishes
before serial preservation verification, with no overlapping LAB mounts.

Ubuntu is current/default, boot ID b3755a7c-c9a0-4f1b-824b-d61545832316.
All 153 baseline EFI files remain unchanged except normal random seed and
the separately archived, authorized entry-090 removal. Retained experiments
are 091/092; manual entry, firmware, four original images and shared payloads
remain. LAB is unmounted; screen-off timer is enabled/active. Installation
left exactly 32 MiB ESP free before retention, so future installation must
account for allocation clusters and entry overhead without lowering the guard.

Next: supply only actual firmware boot inputs before original init's own UDID
hook, preserving valid existing identities and native checks. The early file
must not expose serial values through exports or error logs. Investigate the
original module result and the device-query stall together; neither real
identity nor networking alone establishes activation. No 093 boot or identity
change has occurred. The full stable interactive desktop goal remains active.
