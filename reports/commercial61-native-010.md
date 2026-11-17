# Commercial 010 — capacity and bounded teardown

Completed one controlled boot on 2026-11-13, 11:07:33–11:10:01 UTC. Ubuntu was observed online with boot ID `261621c8-c4af-4161-9496-9ec8fe692b08`. This is not a working-desktop result.

## Verified improvement

- Original commercial init, services and libraries remain in use. The supplied ISO identifies itself as 6.0.0.110/API 20; no SDK userland is substituted.
- The guest admitted the run with 15,741,024 KiB total and 14,893,540 KiB available memory. Its fresh volatile data filesystem was actually expanded to 8 GiB (usable capacity 8,437,198,848 bytes).
- The captured log contains no ENOSPC/database-full errors and no unsupported-SA-511 failures. Original SceneBoard installation completed successfully at 34.124 s; installation success is not proof its desktop process displayed anything.
- The 90-second target timeout and deliberate target termination are recorded. Ubuntu subsequently returned. A final `STOPPED`/cleanup-status record was not captured, so the exact 15-second cleanup outcome is not claimed.

## Still blocked

The original L410/Mali RenderService backend still fails to create its GPU context on FD690. No commercial desktop or physical input acceptance has been obtained. Separately compiled Mesa 013 and own hardware bridges 014 have only offline provenance/link checks; they were **not** deployed in this run.

## Preservation

59 evidence files match their remote hashes. Retrieval mounted the evidence partition read-only with `noload`, then unmounted it; no original journal replay was performed. Post-return verification confirmed all four commercial images still match the supplied ISO, Ubuntu remains current/default, no one-shot entry remains, the custom screen-off timer is disabled/inactive, and the earlier manual GPU entry remains. Of 108 prior EFI files, only systemd-boot's legitimate `loader/random-seed` rotation changed; it was not restored.

See `commercial61-native-010/runtime-analysis.json`, `runtime-evidence/retrieval-manifest.json`, and `post-return-verification.json` for evidence. Completed operational experiments must not be repeated or their records overwritten.
