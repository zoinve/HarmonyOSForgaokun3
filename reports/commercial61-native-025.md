# Commercial desktop 025 — bounded EGL call-boundary diagnostics

024's locally bound own bridge did not remove the actual original application's `EGL_BAD_DISPLAY` or black scanout. This candidate adds observation, not another proposed rendering fix.

Only our bridge is instrumented. It reports entry platform, Mesa handle/symbol availability, the actual DRM-open result, GBM device and Mesa display return. It uses the existing original `HiLogPrint` interface, at most 64 messages per process. It preserves `errno`, does not call `eglGetError`, creates no application-writable files, and changes no original failure/return decisions. Missing logging support is not treated as application success. The native logger test checks the actual compiled helper's limit and errno preservation; it is not target GPU proof.

The original frontend, mapper, commercial libraries/packages, authentication, application sandbox, seccomp, credentials and original source images remain unchanged. The bootstrap matches 024 exactly. The three adaptation references remain the basis documented in the prior reports; no reference test's root identity or sandbox bypass is imported. This is not SDK userland.

Eight scoped offline regressions pass; the full collection of historical operational scripts was not rerun. Ordered archive extraction matches the complete candidate, including all parent directories, modes and bytes. The final overlay is 735,815 bytes, SHA256 `c58399df35c59f15a389ff959cf4cac488751f53c783ee4d3696bc2114bc3459`.

Deployment retains trusted 192-network SSH, standard Ubuntu default and return checks, enabled/active Ubuntu screen-off timer, 32 MiB EFI reserve and original-image hashes. Diagnostics retain 8 GiB volatile data, memory admission, 90-second target budget, 210-second outer deadline and 15-second bounded final cleanup; software deadlines do not guarantee recovery from a kernel hang.

Installation succeeded: both non-PID1 guards refused with exit 77, all 114 prior EFI files were unchanged, and 224,899,072 bytes remain free. Ubuntu default, the manual entry and enabled screen-off timer remain intact. Installation itself selected no one-shot entry and requested no reboot. A separate single bounded diagnostic attempt has now been launched.

## Actual result

The single run completed on 2026-11-13 UTC, 16:42:49–16:45:18 (local November 14). All 59 exported files matched their remote hashes; original evidence retrieval used `ro,noload` and unmounted the partition afterward. Original SceneBoard runs, but all three real scanouts remain black. No desktop success is claimed.

There are **no `EGL025` diagnostic records** in the retrieved evidence. This cannot identify which EGL boundary failed or establish that the provider was not loaded. Investigation of the original commercial `libhilog.so` found that the instrumentation's `LOG_CORE` domain `0x00D02510` is rejected by its unsigned domain gate before emission. Its accepted core range is `0x0D000000`–`0x0D0FFFFF`; the native fixture had not tested this real domain restriction. Correcting our domain does not require altering any logging policy or application permission.

Post-return verification confirms standard Ubuntu current/default, boot ID `c119da77-61ae-4d16-8022-8a50494a2fcf`, enabled/active screen-off timer, retained manual entry, unchanged firmware and all four original commercial image hashes. Of 114 prior EFI files, only the boot-managed random seed rotated. Historical logs and JSON remain unchanged; this attempt is not repeated.
