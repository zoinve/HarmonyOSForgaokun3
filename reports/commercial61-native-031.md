# Commercial 031 — real EGL copy source/destination observations

030 established that the latest exported black frame was fresh and the actual composer client DMA buffer was already black. The remaining boundary is upstream: RenderService rendering versus the own EGL bridge's copy into the original buffer queue.

031 samples nine real RGB pixels from the default back buffer before the unchanged blit, and nine from its actual destination afterward, at most eight copies per process. It also records the original read/draw FBO identifiers. The probe preserves read FBO/buffer, pixel pack buffer and packing state, and errno. No test image is drawn, no GL error is consumed, no authentication or service identity changes, and no original commercial frontend/library is replaced. Zero samples alone cannot prove successful `glReadPixels`: error consumption is deliberately avoided, so these observations must be interpreted alongside actual buffer and rendering evidence.

The native fixture verifies actual probe state restoration, RGB counting with alpha ignored, incomplete-FBO rejection and bounded image geometry. It is not a target GPU test. All public bridge exports and the original commercial runtime closure remain unchanged. The 030 composer observations and bootstrap are retained byte-for-byte. The three adaptation references remain the baseline; the real commercial desktop remains the first acceptance goal before WiFi, touch, USB and external-video work.

Runtime evidence is pending. Numbered prior operations remain closed and immutable. Strict trusted SSH, original image hashes, Ubuntu default boot, enabled/active screen-off timer, RAM admission and the 90-second target / 210-second outer software deadlines remain required. Software deadlines do not guarantee recovery from a kernel or hardware hang.

## Offline verification

All 16 scoped regressions passed, including the compiled pixel-probe fixture, the previous return/forwarding/quota/domain fixtures, real child timeout/RAM checks and screen-off checks. Historical operational collections were not rerun. All five assembled 031 workflows passed syntax and trusted-address/state checks. The bootstrap is byte-identical to 030. The new own EGL implementation is 88,376 bytes, SHA256 `2cacc6b84c8ac4c07c583468e8e9c9f7946276c032a1afd1cf7103d4801005ee`, with identical public exports and no SDK runtime libraries.

The final overlay is 771,606 bytes, SHA256 `9876cb8230d44570b41f08b904f84bc4c8a89798423d2c6a912d208d30ccd177`. Ordered 001 base → 017 directories → 016 hardware → 031 final extraction matches the full build byte-for-byte and mode-for-mode; hardware parent directory ordering is preserved. These checks do not prove target rendering or a working desktop.

## Installation

Installation succeeded with both non-PID1 execution guards refusing with exit 77. All 126 existing EFI files remained unchanged; free EFI space is 220,352,512 bytes. Ubuntu default, the manual entry and enabled screen-off timer were preserved. Installation did not select a one-shot entry or reboot. A separate single bounded 031 run has been launched; its guest evidence is pending.

## Actual result (closed)

The single run completed on November 13 UTC (November 14 local), 17:54:02–17:56:54. All 59 retrieved files matched their remote hashes; the evidence partition was mounted read-only without journal replay and then unmounted. Configured target termination was observed. The three real exported frames remain black. This attempt did not start SceneBoard: the normal CLI request at guest 39.719 s encountered `Bms not ready` and error 10104001 despite shell exit 0. The actual BMS helper publication completed at 40.046 s. Package installation had already succeeded; the scan-ready parameter alone was insufficient to guarantee service publication.

The six actual EGL copy observations were early boot only: default and destination samples were black, with saved read/draw FBO zero. They do not establish the desktop rendering result because no SceneBoard process existed in this attempt. The original readback caveat remains applicable. A bounded retry of the ordinary authorized Ability Manager request is the next correction, not fabricated service readiness or relaxed permissions.

Preservation verification passed: standard Ubuntu boot `98412f1e-f478-44f7-939c-802966074bdf`, unchanged default/firmware/manual entry, unmounted evidence partition, all four original image hashes and enabled/active screen-off timer. Of 126 earlier EFI files, only the legitimate boot-managed random seed changed. No desktop is verified. Numbered runtime logs and JSON evidence remain unchanged.
