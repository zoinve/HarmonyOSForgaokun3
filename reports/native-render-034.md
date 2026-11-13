# 034: bounded NEON rotation/copy-reduction trial

## Scope and safety

The user requested automatic exit from HarmonyOS and autonomous rendering work after cursor adaptation. 033 completed one unattended run and returned to Ubuntu. 034 retains its 240-second target budget and independent 420-second software reboot fallback. These are not hardware watchdogs and cannot recover a wedged kernel. Ubuntu remains the default; only a one-shot trial is selected. Existing manual entries and all numbered evidence remain intact.

The physical touchpad was not operated during unattended testing. Adapter loading alone does not prove visible cursor motion or physical click handling. Status-bar layout is unchanged pending a full-screen photograph. No synthetic input, invented identities, permission bypasses or host security changes are introduced.

## Change

The new composer retains 032's cursor bridge, private clean background, back-buffer selection, DMA ownership, fences and page-flip completion handling. It changes only the full-size landscape copy helper:

- Copy DMA input to cacheable RAM as before.
- Rotate using a 32×32 tiled ARM64 NEON 4×4 transpose, preserving channel conversion and forced opaque alpha.
- Write directly into the retained clean background, eliminating one full-frame intermediate copy.
- Keep the original cached/scaling implementation for non-1:1 geometry.

This is **CPU NEON acceleration**, not GPU rotation. GPU submission already uses the FD690 path; 033 still measured a substantial CPU copy/rotation stage. Stable 120 FPS is not established.

## Verification before boot

Host ASan/UBSan pixel tests cover odd dimensions, full panel size, RGBA/BGRA conversion, bounds and untouched padding. Integration tests compare 72 geometry/crop/scaling/format combinations against the original implementation. A real ARM64 Ubuntu run verifies NEON pixels and measures cached-RAM rotation: old tiled reference 6.081 ms, new 3.115 ms. This microbenchmark excludes full DMA/composer costs and must not be presented as desktop FPS.

The independently built OHOS composer links with no undefined symbols. Its two cursor adapter libraries are byte-identical to 032-r2. The full candidate passes nine artifact hash checks; both native non-PID1 guards refuse execution with exit 77.

## Installation and runtime evidence

034 uses the immutable 032 base initramfs plus a 337,519-byte second archive replacing exactly `/init` and the composer library. Archive comparison proves every other installed member remains identical to the base, including its empty volatile scratch filesystem. No existing EFI files are deleted or overwritten. All 98 pre-existing EFI file hashes, firmware entries and Ubuntu default remain unchanged after installation. Free EFI space: 40,337,408 bytes.

The installed entry is **HarmonyOS 034 - NEON render - AUTO RETURN 7 MIN**. The installed overlay SHA256 is `c1235a1adef476eb623247e84a2eb1840abd4b3462f09f0a94002b31645a908b`.

At initial report creation, the single bounded operational attempt is running. The authoritative outcome will be recorded separately in `native-original-graphics-boot-034/boot-observation.json`; recovered evidence and the deduplicated stage comparison must be examined before any runtime improvement claim.

## Completed single-run outcome

034 returned automatically to Ubuntu, boot ID `339e9762-2361-4314-88d9-128b9096dc8e`. The default remains Ubuntu, no one-shot remains selected, and automatic screen-off is active. Read-only, no-replay retrieval recovered 71 files from `native-interactive-034-55a24162-6f72-4fbf-b473-fcb71eb3a52d`; every remote/local hash matches. The original partition was unmounted afterward.

Deduplicating cumulative snapshots yields 43 distinct copy/rotation samples for each run: 033 mean 28.417 ms, median 27.459 ms; 034 mean 22.061 ms, median 21.526 ms. Mean stage speedup is 1.288×. GPU submission remains approximately 4.67 ms and FD690/Freedreno is active. These are bounded mostly-idle startup runs with capped timing records, not an interactive frame-rate benchmark. The new chain still exceeds the 8.33 ms frame budget before accounting for other work; stable 120 FPS is not achieved. Physical cursor motion/click acceptance and status-bar layout remain unverified.

The next diagnostic separates DMA-to-RAM copy, NEON rotation and background-to-scanout publication. Do not rerun or overwrite completed 033/034 operational evidence.
