# 032 — physical touchpad and status-bar investigation (not a repair release)

## Requested outcome

Make the detachable keyboard's physical touchpad usable in HarmonyOS and correct the incomplete status-bar display. Preserve Ubuntu/default startup, automatic screen-off, original images, 031 and all previous evidence. No automatic reboot or injected input is required or authorized by this investigation.

## Evidence preserved

The device had returned to Ubuntu, boot ID `9a96528a-b256-4064-8c47-ed9ebf3a9ec8`. The original LAB partition was inspected using a separate read-only, `noload,nodev,nosuid,noexec` mount at `/mnt/harmony-input-audit-032`; no journal replay or filesystem repair was performed. The new run is `native-interactive-031-8421541d-af4c-4710-baae-4b2f33428191`.

Its 56 phase logs and two continuous streams are retained in `native-touchpad-statusbar-032/original-031.tar` and `raw/`, with a local per-file retrieval manifest. Both continuous streams have no NUL bytes. Hilog SHA256 is `de66666b4fd6f98b2f94a6794139dd1dde2fab913e961470537bfd03cbd28f55`; fault-stream SHA256 is `55788f44b86b55943e38a61d06618ec7f0ec03fa2e82a0a23c9a476e80c98a31`. These local hashes were freshly checked. A subsequent SSH connection timed out before remote hash comparison; this comparison remains pending, not passed. The read-only mount may remain mounted.

## Touchpad: established facts

- The actual USB `12d1:10b8` touchpad is enumerated by the kernel, opened by libinput and registered successfully with MMI as device 9 in this HarmonyOS run. Ubuntu uses a different event number; hard-coding its event number would be incorrect.
- At approximately 159.527 seconds, physical touchpad activity generates a touchpad-active event. At 159.550 seconds, MMI routes move event 1335 and enter-window to Settings PID 3947/window 84. Settings receives the movement; subsequent movement is also logged. Thus absence of any touchpad input is not supported by this run.
- This does **not** establish physical click, tap-to-click, drag or gesture correctness. Those paths remain unverified.
- The SDK cursor adapter exports `GetPointerInstance` and instantiates `EmulatorPointerDrawingManager`. Static examination confirms that virtual slot 2 (`DrawPointer`, as called by the original MMI server) and slot 14 (`SetPointerLocation`) both point to the same bare `ret` instruction at VA `0xbe84`.
- `GetCursorSurfaceId` at `0xdac4` sets the output ID to zero and returns zero. The screen reports hardware cursor support as zero. There is therefore a concrete missing native cursor-drawing implementation, independently of whether other click issues exist.

The adapter SHA256 is `03e64bcecc882791855ec26840cfbfc8c4763e40e0e1612a677fd0d52b335d3e`. Focused disassembly, including actual MMI virtual dispatch offsets 16 and 112, is retained in `native-touchpad-statusbar-032/cursor-abi-audit-032.txt`. The read-only audit is reproducible using `python next-experiment/audit-native-touchpad-statusbar-032.py`. It audits facts; it is not a runtime regression test or an implementation.

## Status bar: cause not yet established

RenderService, DisplayManager and SceneBoard agree on logical 2560×1600. The native panel's 1600×2560 scanout is intentional because the composer rotates landscape client content. Swapping the logical resolution solely because of physical DRM dimensions would risk breaking working touch alignment.

SystemUI nevertheless logs `width: 2560, height: 1600, landscape: false, orientation: 0`. This is a discrepancy to trace, not yet proof of clipping. Default density is 1.9 (304 DPI); cutout falls back to an empty rectangle. Several status-bar plugins are discovered and the PC `WINDOWS_STYLE` layout is used. Missing service/plugin content must be distinguished from an off-screen or clipped layout. A full-screen photograph showing the incomplete region is needed to resolve that ambiguity.

## References and next implementation boundary

All three required references were considered: L410 HarmonyOS adaptations, L410 Linux compatibility platform and the pinned HarmonyMac checkout (see `reference-three-projects-001.md`). No matching native cursor adapter implementation was found there. The Linux platform's Wayland cursor transport is not itself a native HarmonyOS solution.

The next change should provide real cursor rendering driven by original MMI cursor position/visibility, retaining original input normalization and application routing. Prefer a correctly attached RenderService cursor surface; any composer-backed alternative must handle idle-screen repaint, old-cursor erasure, landscape coordinates, synchronization and visibility without modifying a scanned-out buffer. Do not invent a successful surface ID, substitute injected input, suppress permission checks or simply return success from missing APIs. Verify actual click events separately rather than treating visible motion as full touchpad acceptance.

No 032 boot candidate or repair implementation has been produced or installed. 031 was not rebuilt, reinstalled or booted by this investigation. Device access became unavailable (SSH timeout); restore access before target-side validation. Application-flash-exit acceptance under 031 is outside these input/display findings and remains unclaimed.
