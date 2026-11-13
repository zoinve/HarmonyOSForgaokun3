# Experiment 949: DRM version-query boundary

No desktop was verified. Do not rerun experiment 949.

## Runtime evidence

Preserved decoded logs: `reports/official-arm-hilog-949-parsed/`.
Raw evidence: `reports/official-arm-evidence-949/`.

All four observed RenderService processes ran as UID 1003/GID 1000,
successfully opened `/dev/dri/card0`, then received NULL from
`drmGetVersion()` with errno 13 (EACCES). The selector subsequently
reported ENODEV because it collapses all rejected candidates to that error.
The root diskless fixture 948 successfully queried the virtio_gpu version,
selected a connector/CRTC, and presented real GPU pixels.

## Read-only original-image inspection

Original `system.img` file contexts assign `/dev/dri(/.*)?` the type
`dev_dri_file`. The original RenderService configuration uses the
`render_service` SELinux domain. Its ordinary chr_file permissions include
open/read/write/map/ioctl, but its extended ioctl whitelist in
`system_common.cil` does not include ioctl command 0x6400 (DRM VERSION).

Read-only examination also covered system.cil, system_developer.cil,
vendor public/public_common/public_developer and
vendor/vendor_common/vendor_developer CIL files, including direct
typeattribute membership closure for render_service and dev_dri_file.
No applicable additional 0x6400 permission was found in that examination.
This is strong evidence for a backend/policy incompatibility, not a
complete query of the policy actually loaded by the guest. No matching
VERSION AVC was found in the preserved serial log. Do not claim that
missing audit output proves permission was granted.

No SELinux query/compiler executables (sesearch, seinfo, secilc) were
available in the checked WSL or MateBook environments. No tools were
downloaded or installed. Original vendor prebuilt policies exist at
`/etc/selinux/prebuild_sepolicy/{policy.31,developer_policy}`.

## Safety boundary

No original image, policy, service identity, activation state or watchdog
was changed during this investigation. Do not suppress the failed query,
fabricate a driver result, grant broad ioctl access, disable enforcement,
or treat fixture success as full-system compatibility.

Experiment 949's own 100 MiB userdata remains for evidence preservation.
Before any subsequent full-system boot, verify preserved evidence and
original-image hashes, then perform exact guarded cleanup of that file
only. Earlier experiment userdata 947/944/941/923 was already cleaned up.
