# Original configuration layers: experiment 082

## Actual result

The original `param get` calls completed with wait status zero at samples 17
and 29. The configuration directory layer was:

```
/usr/system:/usr/system/variant/pc/base:/usr/system/variant/pc/china:/sys_prod
```

The follow-X rules listed the original telephony/carrier JSON rules. Raw output
retains kernel-console interleaving. The bootstrap mounts the original system
image at `/usr` and links `/system` to `/usr/system`; therefore this result does
not, by itself, identify an incorrect or absent configuration layer.

Original SAMGR still reported SA511 unsupported. Its original binary's return
1002 follows a failed profile-table lookup. The original `installs.json` is
present, but neither the parameter output nor a root observer's file read proves
which directories SAMGR selected or which profiles its parser accepted.

## Evidence and preservation

- Independent evidence: `reports/original-graphics-boot-082-independent.json`.
- Serial SHA-256:
  `a160bd833721df001a8764ea7305540d6c4ad7d0cc7892524c3d26588bc33bff`.
- All 48 observed SELinux samples were permissive; support and original policy
  remained present. Original service identities were retained.
- Independent checks preserved all 12 provider ELFs, the real ashmem module,
  initrd, virtual kernel, all three original SDK images and 378 prior native logs.
- Real composer hotplug callback completed. No Foundation critical fault or guest
  reboot was observed within the bound. Desktop/readiness/physical display remain
  unverified; previous virtual output is not a desktop-success claim.
- No MateBook/Ubuntu operations or host security changes were performed.

## Next bounded diagnostic

083 adds a guarded, read-only public `GetCfgFiles("profile")` diagnostic in a
separate, explicitly labelled bootstrap caller. It records returned candidates
and readable directory/file information; it is **not SAMGR** and cannot establish
SAMGR's exact view or parser outcome. Its compilation succeeded without executing
the target ELF. The isolated 083 run is pending at this report's creation.
No profile injection, manual BMS directory/database creation, identity changes or
permission/signature/privilege-check bypass was applied.
