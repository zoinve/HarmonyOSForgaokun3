# Original BMS startup evidence — experiment 080

## Outcome

The original Foundation log query now uses the supported `hilog -a 600 -P PID`
command. Its startup records identify a more specific failure than the subsequent
missing database: genuine `InstalldClient` reports **“Load system ability 511 failed
with 1002”**, followed by proxy acquisition failure and directory/install operations
returning **10027408**. A working desktop remains unverified.

- Evidence: `original-graphics-boot-080-independent.json` and the preserved serial
  output under `baremetal-sdk-original-init-qemu-080`.
- Serial SHA-256:
  `9c2d57768564d7361e996eea5c711d5eda9d6502d2dbc17cced834e007e5861b`.
- All 48 observed SELinux samples were permissive. Real hotplug callback completion
  was observed; neither a Foundation critical fault nor a guest reboot was observed
  within the bounded run. These observations do not establish service readiness.
- Independent verification retained the actual scanout/image checks, 12 provider
  files, genuine ashmem module, initrd, kernel, all three original SDK images, and
  all 378 prior native raw files. No MateBook/Ubuntu operation was performed.

## Why no manual directory or permission fix was applied

Read-only inspection of the genuine BMS library identifies its intended directory
creation flow: `CreateBmsServiceDir` delegates the new BMS directory to the original
installd client. The real path is
`/data/service/el1/public/bms/bundle_manager_service`; this is not an instruction to
manufacture its database or bypass the original installation service.

The original SDK contains `/system/profile/installs.json` declaring on-demand SA
511. A read-only audit of the original SAMGR executable (SHA-256
`38cd27e742fec1504a4f443fe92e3154d53363ae6f94617ea4a91d8781de496b`)
confirms that its `LoadSystemAbility` calls `GetSaProfile` at `0x6c688` and branches
to return 1002 at `0x6c898` when profile lookup fails. OpenHarmony 6.0's public
`PROFILE_NOT_EXIST=1002` definition agrees, but the original binary, not an assumed
upstream version, is the relevant evidence here.

The file's presence in the SDK does not prove that the running SAMGR discovered
and parsed it. Its original loader obtains profile directories through
`GetCfgFiles("profile")` and calls the genuine profile parser. No replacement
profile, fake SA registration, caller identity, or permissive parameter ACL was
introduced.

Other genuine installation failures (including signature, extension privilege,
and system-capability checks) remain separate unresolved findings. They were not
disabled and must not be attributed automatically to the SA 511 failure.

## Next experiment

081 keeps the working graphics stack and original services unchanged. It adds
bounded original SAMGR startup-log queries and read-only inspection of
`installs.json` through that process's own root in the isolated VM. Its run is
pending at the time of this record; no outcome is presumed.

Historical 080 marker text still says `tail=200`; the actual argv was `-a 600`, as
recorded in the numbered preparation source. Raw evidence and completed launchers
were not rewritten to conceal this diagnostic-label mismatch.
