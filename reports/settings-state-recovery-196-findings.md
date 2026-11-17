# Settings recovery candidate: progress188-196

## Actual result

An independent local 8 GiB data candidate is prepared, unmounted and offline
fsck-clean. It has NOT been transferred to the MateBook, installed, selected or
booted. No Settings UI success or original-verifier installation success is
claimed. Active persistent-data165, desktop173, target EFI entries and USB work
have not been changed by this work.

Candidate: /home/zoinve/harmony-virgl-883/settings-data-candidate-191-r2/data.ext4
UUID: b8383c4f-844b-46cc-9d67-34a3745b3f1f
SHA256: f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce
Bytes: 8589934592; allocated locally: 2817458176.
The existing native persistent-data guard requires full allocation on the
target filesystem. Do not relax that guard or point it at active-data165.

## Matching original state

188 verifies the supplied BMS main/slave Settings records each have exactly one
matching user100 application token in their corresponding source token DB.
The supplied resources.index, libc++_shared.so and libnative.so are byte-identical
to their entries in original Settings.hap. These are consistency observations,
not cryptographic signature verification or proof of executable compatibility.

189 prepares a private allowlisted original-install-state archive. All 2722
entries were reread and compared by content hash, UID, GID and mode. Only code,
BMS and access-token installation-state subtrees and their real ancestors are
included. Separate account, activation, startup identity, network-authentication
and optional Debian-root subtrees are excluded. No application user-data tree
is imported. Whole original BMS/token records are preserved, not fabricated.

190 preserves 2600 existing source labels and resolves the remaining122 through
libselinux using the original system file_contexts. All2722 candidate labels
are applied and read back. The original policy and host security configuration
are not changed. GNU tar warns that its LIBARCHIVE xattr header is unknown;
explicit label application/readback, not that ignored header, proves coverage.

## Provider ownership correction

The existing minimal seed123 was fetched over authenticated, read-only SSH and
verified against its original SHA256. Initial191 failed during resize before
mounting. Revisionr1 uses the proven165 pre-resize fsck sequence, but correctly
refused to infer a SettingsData owner for user100. Both failed candidates remain.

192 reads the unmodified supplied BMS record: SettingsData is singleton/user0,
UID20027. The minimum seed's real database files belong to UID20002. Revisionr2
uses the actual source registration and verifies its source application token.
It reowns only five nodes within that application's candidate database tree.
Both SettingsData database hashes remain exactly those of123; original BMS and
token database bytes are unchanged. No UID/token registry values are invented.

## Device-marker audit

193-195 conservatively record unresolved permission device_id values rather
than relabel them as hardware IDs. Follow-up196 resolves all2496 rows to the
public constant PHONE-001; all145 HAP token device_id values are0.
OpenHarmony security_access_token, OpenHarmony-6.0-Release commit
53287abcc13b418c091154fdb629c37dcfa34ce6, data_translator.cpp explicitly writes
PHONE-001 into this permission storage field. hap_token_info_inner.cpp writes0
for stored local HAP token information. The supplied commercial
libaccesstoken_manager_service.z.so contains the same marker. This supports a
fixed schema-marker interpretation; the public branch is not asserted to be
byte-identical to the commercial build, and literal presence alone is not a
complete binary code-path verification. No marker or device identity is rewritten.

## Remaining acceptance

The original missing-signing-block rejection153 and absent-bundle launch173
remain valid historical evidence. Matching preinstalled state does not replace
signature verification. A bounded isolated candidate boot must retain the
original verifier, authentication, real device identity, Ubuntu default, return
watchdog and original image hashes. Retain byte-identical desktop173 runtime
where possible; configure a NEW candidate data path/UUID, never data165.
Do not transplant one record into active BMS, re-sign Settings, weaken checks,
substitute PCSettings, or claim restored installation before original services
and an actual usable MainAbility window establish it.

34 explicitly counted analysis/helper tests passed in one aggregate run. Their
scope is data selection, privacy, metadata/label guards and offline construction,
not native app launch or hardware-driver acceptance. USB remains paused at181.
