# Commercial desktop 024 — local EGL bridge function binding

## Hypothesis and bounded change

023 successfully initialized the original mapper and SceneBoard root scene, but actual scanouts remained black and SceneBoard reported invalid EGL displays. Its original commercial EGL frontend loads our implementation provider, whose internal `eglGetDisplay` call used a preemptible PLT reference to another publicly exported EGL entry.

The offline characterization and actual AArch64 disassembly are recorded in `commercial-egl-024.md`. 024 relinks **our provider only** with local internal function binding. The source, public exports, original commercial frontend, application packages, sandbox, authentication, service identities and all original images remain unchanged. No optional hook library is fabricated or skipped. SDK headers remain compiler inputs; no SDK runtime libraries replace the commercial runtime.

Both existing copies of the provider (system and vendor passthrough RAM overlays) consume the same newly linked file. The bootstrap is byte-identical to 023. The ordered initramfs chain remains 001 base → 017 directories → 016 hardware → 024 final, verified against the full build for member bytes, modes and parent hierarchy. Final overlay: 734,811 bytes, SHA256 `435345b91c9b1bbe75437936e55281efb46fc786e6311ee2ddc0641e26de6a4d`.

Eight scoped offline regressions passed. All five operational workflows parse and retain strict trusted 192-network SSH; installation and post-return checks require standard Ubuntu rather than reusing the previous S4 diagnostic session exception. Screen-off must be enabled/active. Original image hashes, manual entry, default boot, 32 MiB EFI reserve, 8 GiB volatile data and memory admission remain guarded. Diagnostics retain the 90-second target budget, 210-second outer deadline and 15-second bounded cleanup; software bounds do not guarantee recovery from a kernel hang.

## Runtime status

Installation succeeded. Both non-PID1 execution guards refused with exit 77; all 112 prior EFI files were unchanged. EFI free space is 225,644,544 bytes. Ubuntu default, original manual entry and enabled screen-off timer were retained; installation itself selected no one-shot entry and requested no reboot. A separate single bounded run is now launched.

## Actual result (closed single attempt)

The single attempt ran on 2026-11-13, 16:32:22–16:35:13 UTC (local November 14). All 59 retrieved evidence files matched their remote hashes; the original evidence partition was mounted read-only with journal replay disabled and subsequently unmounted. Configured target termination was observed.

Original SceneBoard PID 3347 runs and reports `initSceneBoard ok`, but still reports invalid EGL display pointers / error 12296 (`EGL_BAD_DISPLAY`). All three genuine P6 160×256 scanouts remain entirely black, with SHA256 `33e39d41124406e5048fd667d3cd7b34e84b29874937bd5efd0d58ff2a8d6260`. **Desktop acceptance remains false.** Local symbol binding was verified offline but did not resolve the observed target failure; its role in the black screen is not established. Optional hook/configuration failures must not be assumed causal without further tracing.

Independent post-return verification confirms standard Ubuntu current/default, boot ID `0ace200b-dd49-43b1-879b-842ec1d74d27`, unchanged firmware, manual entry, all four original commercial image hashes, unmounted evidence partition and enabled/active screen-off timer. Of 112 prior EFI files, 111 are unchanged and only the boot-managed random seed rotated. Historical logs and JSON results are preserved; this attempt will not be repeated.
