# Commercial desktop 026 — valid diagnostic HiLog domain

025's bounded instrumentation used a core logging domain that the original commercial logger rejects. Consequently it produced no EGL boundary evidence; it did not establish a Mesa/DRM/GBM failure location.

026 corrects only our diagnostic domain to `0x0D002510` and assigns unique diagnostic labels. The 64-message per-process limit, errno preservation and original EGL return decisions remain. No global log filter, original frontend, mapper, service identity, sandbox, authentication, seccomp or permission is changed. The three-reference adaptation baseline and original commercial userland remain; this is not an SDK-runtime substitution.

The regression models the exact original AArch64 unsigned domain gate, rejects the old value, accepts the corrected value and checks both accepted-range boundaries. The previous compiled helper limit/errno test remains applicable. Static evidence is not target logging or desktop proof.

Deployment retains original images, standard Ubuntu default/return, enabled/active screen-off timer, trusted 192-network SSH, 32 MiB EFI reserve and the existing bounded diagnostic budgets. Runtime results are pending; success requires original desktop integration and real desktop pixels. Closed earlier attempts and their logs are not repeated or overwritten.

Nine scoped offline regressions passed, including the corrected domain gate and compiled bounded logger fixture. The bootstrap remains byte-identical to 025. The complete ordered archive and parent/mode/byte comparison passed; the final overlay is 735,821 bytes, SHA256 `d2204716e92052c5f3ef95fcec327c0c7fa5bb8b782fb10b651c5a8fb2b7b5b3`. These are offline checks, not target logging or rendering evidence.

Installation succeeded: both non-PID1 guards refused with exit 77, all 116 prior EFI files were unchanged, and EFI free space is 224,153,600 bytes. Ubuntu default, manual entry and enabled screen-off timer were retained. Installation itself selected no one-shot entry or reboot. A separate single bounded 026 diagnostic run is now launched; runtime evidence remains pending.

## Actual result — closed

The single run returned to standard Ubuntu on 2026-11-13 at 16:54:17 UTC (local November 14). All 59 exported files matched their remote hashes; retrieval used read-only `noload` access and unmounted the partition. The original SceneBoard process runs, but all three actual 160×256 captures remain black. No desktop success is established.

The valid domain produced 192 diagnostic events: exactly 64 `mesa` events each from RenderService, theme manager and SceneBoard. Each records a non-null Mesa library handle. Frequent symbol resolution exhausted the shared quota before later stages could log; their missing messages therefore do not identify a display/DRM/GBM failure. Saved errno values are not return codes.

Post-return verification preserved all four original image hashes, firmware, standard Ubuntu current/default, manual entry and enabled/active screen-off timer. Of 116 prior EFI files, 115 are unchanged; only the boot-managed random seed rotated. LAB is unmounted. This run and its numbered logs are closed and will not be repeated.
