# Commercial desktop 028 — initialization and presentation boundaries

027 established that the actual SceneBoard process obtains a non-null Mesa display through real DRM and GBM, but all three captured frames remained black. That is not desktop success or evidence that initialization succeeds.

028 changes diagnostic annotations only in the own board EGL bridge. It observes initialization, configuration queries, context/pbuffer creation, and window-surface/current-context/swap entry alongside the six existing stages. Each of 19 known stages has eight messages per process (152 maximum). Original return values and fallback decisions remain unchanged; the compiled native fixture checks single invocation, result/fallback and errno preservation. No diagnostic calls `eglGetError` or grants filesystem access.

Original commercial EGL frontend, services, mapper, packages, authentication, sandbox, seccomp and identities remain unchanged. The three-reference adaptation baseline is retained. No SDK runtime replaces the original commercial runtime. The bootstrap is byte-identical to 027.

Eleven scoped offline regressions passed, along with assembled workflow and trusted SSH checks. Ordered archive parent/byte/mode validation matches the full build. The final overlay is 736,581 bytes, SHA256 `5868f4530af010622cedfe46ab80e9aa1698956a4bfeeca01854af15b05a881d`; the chain remains 001 base → 017 directories → 016 hardware → 028 final. Historical operational experiments were not rerun as a test suite.

Installation succeeded: both non-PID1 guards refused with exit 77, all 120 previous EFI files were unchanged, and 222,662,656 bytes remain free. Ubuntu default, manual entry and enabled timer were retained. Installation selected no one-shot entry and requested no reboot. A separate single bounded run has now been launched; guest results remain pending.

The 8 GiB volatile data, memory admission, 90-second target budget, 210-second outer deadline, 15-second cleanup bound, original image hashes, 32 MiB EFI reserve and enabled/active screen-off timer guards are retained. Software bounds do not guarantee recovery from a kernel hang. Genuine desktop pixels and original desktop integration remain required; no success is claimed.

## Actual result (closed)

The single run completed on 2026-11-13, 17:11:33–17:14:00 UTC (local November 14). All 59 exported files matched their remote hashes; retrieval used read-only `noload` and unmounted the evidence partition. Configured target termination was observed. SceneBoard PID 3572 ran, but all three actual 160×256 scanouts remained entirely black. Desktop acceptance is false.

The actual SceneBoard trace establishes non-null Mesa/GBM display handles, successful `eglInitialize` and `eglChooseConfig` returns, and non-null contexts on two threads. Configuration counts were not captured. `eglMakeCurrent` was entered, but this annotation does not establish its return value. No SceneBoard window-surface or swap entry was captured; these may occur in RenderService instead. Optional original frontend hook/config warnings are therefore not established as the cause of the black screen. Further investigation must include application content and scene submission, not assume EGL initialization failed.

Post-return verification confirms standard Ubuntu boot ID `2d95bb69-d663-45dd-b6b0-dcee45664922`, unchanged current/default boot selection and firmware, retained manual entry, unmounted evidence partition, and enabled/active screen-off timer. All four original commercial image hashes are unchanged. Of 120 prior EFI files, 119 are identical; only the legitimate boot-managed random seed rotated. Historical logs and JSON evidence remain unchanged.
