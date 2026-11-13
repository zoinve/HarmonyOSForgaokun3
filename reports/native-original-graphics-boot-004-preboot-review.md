# Native original graphics 004 — isolated umask correction

003's diagnostic PID1 calls `umask(077)`, inherited through clone and exec.
Bootstrap requests 0755 for OverlayFS upper directories but does not reset that
mask. OverlayFS exposes upper root metadata, thus 0700 prevents unprivileged
service traversal even when original executable and interpreter are 0755.

`native-overlay-umask-regression-004.json` records a disposable native mount
namespace regression: mask 077 gives overlay root 0700 and unprivileged X_OK
failure; 022 gives 0755 and succeeds. No original images, target programs, GPU,
or host policy were used by that regression. This establishes the DAC defect;
the original service outcome still requires the separate native trial.

004 changes only the target namespace child to `umask(022)` before bootstrap;
the outer diagnostic logger retains 077. Additional pre-init stat diagnostics
record actual overlay, executable and interpreter modes. Original service
credentials/configuration, read-only source images, permissive target SELinux,
rooted namespace, RAM data, 70-second observation and 180-second outer return
remain unchanged. No critical-service checks are disabled.

Nine build artifact checks and two real native non-PID1 refusal checks pass.
The install preserves Ubuntu default and firmware entries. It removes only
the unreferenced old EFI cache `harmony-native-diag-007/initrd.img`, after
hash comparison to the retained original LAB build archive. Both are SHA256
`d0a16f3db2fcc42837783ca704fa6cfd448b301a84c1bdb96fc24f0b4e887bb2`.
The original archive and all numbered logs remain. Post-install ESP free space
is 77,553,664 bytes; 81 other existing EFI files are unchanged. The historical
installer result key `deleted_obsolete_kernel_caches` contains this initrd path,
not a removed kernel; the path and journal, rather than the legacy key name,
identify the exact deletion.

All three pinned adaptation references and the native Freedreno bundle remain
unchanged. No emulator board configuration, fake boot events, private-service
substitutes, altered Ubuntu LSM, persistent default change or desktop claim.
The one-shot trial is new evidence, not a rerun of 001–003.
