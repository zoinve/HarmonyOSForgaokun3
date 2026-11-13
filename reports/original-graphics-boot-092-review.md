# Original graphics / desktop observation 092

## Verified outcome

The later original desktop request still failed. Original Foundation did request
`com.ohos.sceneboard`, but authentic AppSpawn replies repeatedly reported
`0xd000008` / `218103816`. This isolates a process-creation failure boundary;
the specific failing stage and meaning of that code remain unconfirmed.

- Original `bm` exited zero but reported failure to get information.
- Original `aa` exited zero but reported ability-start failure / `10108101`.
- Allocated child PIDs and CLI exit zero are not successful application startup.
- All five independently checked 1280×800 scanouts (120, 360, 480, 600, 650 s)
  were entirely black. RGB SHA-256:
  `76ed5c9c326ba62322d464a22d3fcf7b76c7352c6d33badc36ccea7a33325e97`.
- No Foundation critical fault or guest reboot was observed within the bound.
  Desktop readiness and physical scanout remain unverified.

An adjacent `CUSTOM_SANDBOX: PERMISSION_DENIED` message and kernel token warnings
are separate leads, not established causes of the AppSpawn reply. No sandbox,
identity, permission, signature or account checks were bypassed.

## Preservation and evidence

`reports/original-graphics-boot-092-independent.json` verifies the original SDK
images, kernel, initrd, twelve graphics-provider files, genuine ashmem module,
configuration-query helper, retained independent 8 GiB test volume, and all
378 previous native raw files. It also checks actual PPM/PNG pixels and CRCs.
All 72 captured SELinux samples were permissive, not disabled.

Serial SHA-256:
`30e86edac3258f331b6f6726386e094c0f5bdffe14fe5ffd31ca1cbf1fcae184`.
The trial and successful verifier were each executed once; evidence is retained.
Everything in this phase ran in local WSL / an isolated virtual-display guest.
No MateBook SSH, Ubuntu boot/security/screen changes, commits or downloads of
executable code were performed. Read-only summary-query mistakes changed no raw
evidence or verification results.

## Next diagnostic 093

Fresh 093 keeps the same providers, original services and 8 GiB test-volume
setup. It adds bounded original HiLog queries for the actual AppSpawn daemon
PID and the `AppSpawn` tag, so short-lived child diagnostics are not excluded by
a daemon-only PID filter. The tag's usefulness must be established by actual
output. Two offline safety tests passed; preparation completed. Runtime and
independent verification are pending at this writing. No error-code mapping or
successful SceneBoard start is claimed.
