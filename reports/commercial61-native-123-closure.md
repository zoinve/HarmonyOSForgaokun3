# Native OOBE Seed 123 Closure

- Run: `commercial61-native-087-8a37e4cd-deb7-433f-bbb0-fdd51847fba0`; completed once. Do not reboot this numbered experiment.
- The seed passed source/destination SHA-256 checks. RAM admission passed with 14594092 KiB available. All five loop devices were configured with the intended sizes and read-only flags (volatile data is writable).
- The original isolated bootstrap exited with `NATIVE_ORIGINAL001_FAIL explicit opt-in/permissive required errno=17`, wait status 28416 (exit 111). The errno field is not independently diagnostic here.
- The installed entry contains all required opt-in tokens, but recovered kernel command-line records lack `harmony.commercial=1`. The excessive accumulated EFI initrd arguments point to command-line truncation; the setup seed itself was not rejected.
- No original commercial services or OOBE ran in this attempt. The reference setup method remains untested on-device with this prepared seed. Desktop success is not claimed.
- Standard retrieval correctly refused a missing identity-diagnostic file. Subsequent read-only/noload retrieval exported only allowlisted early markers and token-presence metadata, with physical serial and hex-identity guards. Raw runtime files remain on the target.
- Evidence: `commercial61-native-123/early-failure.json`, `early-bootstrap-failure.json`, `cmdline-admission-audit.json`, `post-return-verification.json`.
- Preservation passed: Ubuntu current/default, firmware, all four original images, manual entry, screen-off timer enabled/active, LAB unmounted. Only the authorized old entry and boot-managed random seed changed.
- Next candidate 124 removes only fully shadowed initrd archives and verifies that the resulting member/mode/content map exactly equals the tested 123 full initrd. Original bootstrap checks, runtime, setup seed and services remain unchanged.
