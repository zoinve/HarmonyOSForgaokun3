# Commercial 035 — distinguish confirmed black pixels from failed readbacks

034's public RS dump requests were rejected by the original permission gate. The checks remain intact; those requests are not repeated. Existing window logs show nonzero desktop bounds and visibility, but actual compositor input and output remain black. 033 found matching public original-frontend/Mesa state. None of this establishes why RenderService's output is black.

Single next hypothesis: earlier zero-initialized GL pixel probes could report zero without a successful read, for example with an incompatible framebuffer sample configuration. 035 compares two reads of each of nine positions into different nonzero RGBA sentinels. Only matching complete RGBA results count as confirmed; no-write, partial-write or changing results remain unconfirmed, never confirmed black. This demonstrates stable writes, not absence of every possible GL error. No GL error is consumed. The original read-FBO/buffer, pixel packing state and errno are restored.

The chosen real Mesa EGL configuration's sample count and sample-buffer count are queried with actual success flags. No configuration is changed and no test image is drawn. The real blit, fences, flushes, return decisions and original service/authentication/sandbox/permission checks remain unchanged. Original frontend and commercial runtime remain intact; no SDK userland is introduced.

The 033 bootstrap is retained byte-for-byte, without the known-denied 034 dump requests. The 032 normal launcher retry, 030 composer and 033 dispatch observations remain. Existing eight-copy observation gating bounds new readback/configuration logs to at most 24 per process, alongside the unchanged earlier trace limits. The fixture tests actual diagnostic code against no-write, partial-write, black and colored results, incomplete framebuffer, state restoration and errno. It is not target GPU or desktop proof.

All three adaptation references remain the baseline. Genuine original desktop pixels precede WiFi/touch/USB/video-output adaptation. Target evidence is pending. Strict trusted SSH, Ubuntu default/manual entry, original image hashes, enabled/active screen-off timer, RAM admission, EFI reserve and unchanged bounded diagnostic return remain required. Software deadlines cannot guarantee recovery from a kernel/hardware hang.

## Offline verification

All 23 scoped regressions passed, including the compiled sentinel-readback fixture and earlier public-dispatch, retry, state/errno, memory admission and real child-deadline checks. Historical operational experiments were not rerun. The five assembled workflows passed syntax, candidate, trusted-address and enabled/active timer checks. The bootstrap is byte-identical to 033, and target/outer deadlines remain unchanged.

The own EGL provider is 93,432 bytes, SHA256 `2aaebc09a568f4707f4e21333743e814f864a17b682c339246f0512b3624239d`. Its public exports and original commercial runtime closure are unchanged. The final overlay is 774,028 bytes, SHA256 `ed91893aa3266b58317551ab2292b4b24bc643b364b7c40808d6cf177d31d900`. Ordered 001 base → 017 directories → 016 hardware → 035 final extraction matches the full build's bytes and modes, including required parent ordering. These checks do not establish target readback validity or desktop rendering.

## Installation

Installation preserved all 134 pre-existing EFI file hashes. Both non-PID1 guards refused with exit 77; free EFI space is 217,223,168 bytes. Ubuntu default, the manual entry and enabled screen-off timer were preserved. Installation selected no one-shot entry and requested no reboot. A separate single guarded 035 diagnostic run has been launched; guest results remain pending.

## Actual result (closed)

The single run completed November 13 UTC (November 14 local), 18:49:35–18:52:27. All 59 retrieved files matched their remote hashes; read-only retrieval did not replay the evidence partition journal and left it unmounted. Configured target termination was observed. Original SceneBoard installation and process were observed, but all three actual PPM exports remain black: no genuine desktop is verified.

All 16 framebuffer observations reported complete framebuffers, nine attempted and nine confirmed stable RGBA writes, with zero nonblack samples. This includes both default-back-buffer and destination observations at approximately 74.82–74.86 seconds, after SceneBoard startup. All eight configuration queries succeeded and reported `EGL_SAMPLES=0`, `EGL_SAMPLE_BUFFERS=0`. Thus this run does not support the failed-readback or multisample-configuration hypotheses. GL errors were not consumed; sampled stable writes do not prove every pixel or identify the upstream drawing failure.

Four deduplicated actual compositor observations likewise show black sampled client input and completed output, latest at 74.871892 seconds. Detailed raw-derived records are preserved in `confirmed-readback-analysis.json`. The next investigation remains upstream in original content rendering, not another unsubstantiated blit or dispatch change.

Return verification confirms standard Ubuntu boot `ae587799-0092-448b-9f44-6d8822c91e71`, current/default entry, unchanged firmware/manual entry/all four original image hashes, unmounted evidence partition and enabled/active screen-off timer. Of 134 earlier EFI files, 133 remained unchanged; only the legitimate boot-managed random seed rotated. All 035 operational steps are closed and must not be rerun or their numbered evidence overwritten.

## Read-only follow-up

See [the broker policy audit](commercial-broker-policy-audit-035.md) for the original broker's concrete security-context startup failure and a timing qualification: the last observed black scanout at 74.871892 seconds precedes SceneBoard's first ArkUI first-frame-message flush at 75.125 seconds. Neither a later displayed desktop nor a post-flush black desktop has been established. No operational experiment or original security check was repeated or altered.
