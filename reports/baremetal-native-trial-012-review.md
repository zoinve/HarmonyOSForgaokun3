# Native trial012 execution ledger

Plan: continue candidate015's already approved render-only composer-method regression.

- [x] Verify all 340 trial011 saved log hashes and fresh Ubuntu/EFI baseline.
- [x] Stage independently verified candidate015; run actual ARM64 refusal checks.
- [x] If required, archive hash-known unreferenced obsolete EFI assets before removal.
- [x] Verify fresh install, one boot-counted attempt, immediate bounded SSH return and collect.
- [x] Independently verify raw logs, method/FD/pixel evidence, Ubuntu default and screen-off.
- [x] Archive consumed entry only after successful evidence preservation.

Ruling: use the existing isolated non-git lab and numbered evidence instead of creating
a worktree or commits; preserve completed operational records and never rerun them.
No GPU payload changes are planned. Full HDI/RenderService and physical scanout remain
outside this method-level experiment; no primary DRM, InitDisplay, Commit or modeset.

Preparation incident: an Add File operation overwrote historical restore-rw-003.py
before the numbering collision was noticed. No historical report or remote state
was changed: its existing-report assertion blocked execution. Moved the new adapter
to unused011; reconstructed historical003 from002/004 and preserved report003's
50-log record, explicitly labeled as reconstructed (not byte-identical original).

## Results

- `baremetal-composer-native-001.json`: all 378 collected file hashes verified,
  including all 340 unchanged historical records and 38 new snapshots.
- Native kernel `7.1.0-rc3-gaokun3-el2`, candidate015, FD690: actual extracted
  reference composer methods accepted the cross-exec DMA-BUF/fence, waited the
  received fence, preserved caller ownership and closed retained descriptors.
  Exact GPU and independently mapped pixels matched; diagnostic exit status 0.
- Render-only sandbox retained: uid/gid65534, no capabilities, no_new_privs,
  private PID/mount/network namespaces, primary DRM absent; no InitDisplay/Commit.
- `baremetal-native-trial-012-independent-verification.json`: returned Ubuntu
  boot `6b46894a-8b4b-49a4-bf71-5a903d6b3d95`, persistent default unchanged,
  no pending one-shot, logical screen already off and automatic timer active.
  Physical screen was not observed.
- `boot-entry-cleanup-010.json`: consumed015 entry archived then removed;
  82 other EFI files unchanged, no raw logs or diagnostic assets removed.
- `archive-obsolete-efi-assets-004.json`: obsolete006 assets archived before
  removal. Failed003 guard attempt preserved and did not modify EFI.

Full target HDI/container ABI, RenderService, policy-authorized SELinux graphics,
physical scanout, initially unsignaled fence behavior and desktop remain unverified.
Next: read-only characterization of the original SDK composer/RenderService ABI;
do not repeat this completed trial or mistake its private C bridge for full HDI.
