# EFI cleanup after commercial test 020

The user requested EFI cleanup before further experiments. Test 020 returned to Ubuntu, boot ID `76c3f9f3-6d5f-44f3-b3c2-8c3b441a8052`. Its independent post-return verification was saved **before** this cleanup, so the intentional cleanup does not invalidate or rewrite historical preservation evidence.

## Scope and result

- Removed 18 obsolete files from old `native-original-graphics-NNN` directories only, after confirming that no current boot configuration references their directory. No kernels or boot menu entries were removed.
- Archived every removed file outside EFI at `/home/zoinve/.local/share/harmony-arm64-kvm-lab/efi-unreferenced-cleanup-001/files`, with SHA256 verification and a durable pre-deletion journal. This is reversible archive cleanup, not deletion of original images or numbered experiment evidence.
- EFI free space increased from **31,113,216** to **286,437,376 bytes**; filesystem space reclaimed: **255,324,160 bytes** (about 243.5 MiB).
- All 102 retained EFI files are byte-identical. All boot configuration files and firmware entries are unchanged. An independent post-cleanup check confirmed all 101 boot-file references still exist.
- Ubuntu remains the current and default entry; no one-shot entry or reboot was requested. The original manual HarmonyOS entry, commercial 020 and every existing menu entry remain. The custom screen-off timer remains disabled/inactive.
- Original commercial images, test logs, backups, Ubuntu/Android firmware and boot loaders were not removed or altered. No new operational test was started by this cleanup.

## Evidence

`reports/efi-unreferenced-cleanup-001/plan.json`, `cleanup.json` and `post-cleanup-verification.json` record the exact file list, hashes verified, before/after space and independent checks. The remote archive contains `before.json`, `backups-verified.json` and `result.json`. Offline scope regression: `python next-experiment/test-efi-unreferenced-cleanup-001.py`.
