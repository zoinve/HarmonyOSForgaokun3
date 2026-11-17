# Commercial 032 — bounded original desktop launch retry

031 exposed a narrow BMS publication race: the original CLI queried before the BMS helper was ready, even though bundle scanning had signalled readiness. The CLI returned shell exit zero while reporting a rejected request.

032 preserves all earlier HUKS/account ordering and readiness checks, and retries the exact ordinary `aa start` command at most six times with two-second waits. It stops on an actual SceneBoard process, never on CLI exit status alone, and returns failure if none appears. Process observation is not desktop acceptance. No readiness parameter, authentication, permissions, sandbox, service identity or application state is fabricated or relaxed.

The 031 EGL observations, 030 composer observations and bootstrap remain unchanged. Original commercial frontend, mapper, packages and runtime remain intact; no SDK userland is added. The three adaptation references remain the baseline. Desktop verification precedes WiFi/touch/USB/video-output work.

The real shell regression covers late readiness, repeated false-success CLI exits, the six-attempt limit and an already-running process. Runtime results are pending. Strict trusted SSH, original image hashes, Ubuntu default/manual entry, enabled/active screen-off timer, memory admission, 32 MiB EFI reserve and unchanged 90-second target / 210-second outer deadlines remain required.

## Offline verification

All 18 scoped regressions passed, including the real shell retry fixture and previous compiled EGL/copy/quota/errno fixtures, real child deadline/RAM checks and screen-off tests. Historical operational collections were not rerun. The five assembled workflows passed syntax and candidate/trusted-address checks. The bootstrap is byte-identical to 031; the EGL 031 and composer 030 provider artifacts are unchanged.

The final overlay is 771,740 bytes, SHA256 `f0d4719426091c36fa002bafb37fe5fa397925e7f7a2805a60682772a2dec661`. Ordered 001 base → 017 directories → 016 hardware → 032 final extraction matches the full build byte-for-byte and mode-for-mode, including hardware parent directory ordering. These checks are not desktop proof.

## Installation

Installation verified all 128 pre-existing EFI file hashes unchanged. Both native non-PID1 guards refused execution with exit 77. Ubuntu default, the manual entry and enabled screen-off timer were retained; EFI free space is 219,570,176 bytes. Installation itself selected no one-shot entry and requested no reboot. A separate single bounded 032 attempt has been launched; guest results are pending.

## Actual result (closed)

The single attempt completed on November 13 UTC (November 14 local), 18:03:09–18:06:01. All 59 retrieved files matched their remote hashes; read-only retrieval used no journal replay and unmounted the evidence partition. Configured target termination was observed. SceneBoard was observed after the first ordinary launch request. Its wallpaper and desktop nodes reached the original RenderService tree at approximately 48.7 seconds. This establishes launch, not a desktop: all three actual exported frames remain black.

The completed scanout at 74.105 seconds still has black synchronized samples in both the real composer input and output (40,960 samples each). Its stable PPM update was exported at 80.188 seconds, so the final black result is not merely a stale early-boot capture. At approximately 74.06–74.07 seconds, the own EGL probe likewise found zero nonblack RGB samples in both the default back buffer and the copy destination, with saved read/draw FBO zero. Because `glReadPixels` returns void and the probe deliberately does not consume GL errors, these nine-pixel reads alone are not validated readback success. Raw-derived observations are preserved in `copy-boundary-analysis.json`.

Investigation therefore continues upstream of the copy, including original frontend GL dispatch and current-context routing. No speculative rendering or security change is justified by black pixels alone. The upstream OpenHarmony 6.0 wrapper's “There is just no current context. skip” message belongs to an already-unbound context-release path; that message alone does not establish a rendering context failure or prove the commercial binary is identical to upstream.

Post-return verification confirmed Ubuntu boot `a4dcd7a8-d6e6-4210-8a7a-6473c37d61b0`, standard current/default boot, unchanged firmware/manual entry and all four original commercial image hashes, an unmounted evidence partition and enabled/active screen-off timer. Of 128 prior EFI files, only the legitimate boot-managed random seed changed. This operational experiment is closed; its logs and JSON must not be overwritten or its operations repeated. **No genuine commercial desktop has been verified.**
