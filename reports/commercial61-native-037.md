# Commercial 037 — correct reference startup order

036 is closed and immutable. Its HarmonyMac pre-launch SA gate kept waiting for WMS and prevented SceneBoard startup within the diagnostic. Read-only comparison found original SceneBoard onCreate at 40.727 seconds in 035 followed by foundation publishing WMS at 44.487 seconds, whereas 036 never published WMS. The correction restores the exact 035 normal account/Ability Manager launch/retry script while retaining 036's L410 private namespace implementation. No original service permission, identity, sandbox or SELinux policy check is changed.

The reference SAMgr probe remains packaged but is not invoked as a launch prerequisite. Its existing provenance file only identifies its source; it is not readiness evidence. 037 does not infer missing-service status from SELinux AVC lines in permissive mode. The original undefined broker-domain failure remains a separate unresolved dependency.

HarmonyMac supplies the normal Ability Manager launch reference; L410 HarmonyOS Adaptations supplies the namespace body with the board-inappropriate Mali/OOBE preloads omitted; L410 Linux Compatibility Platform supplies the later AnCo/Wayland integration scope and does not replace original service startup. Pinned references remain those in reference-three-projects-001.md.

Candidate build and the 037 regression checks passed: bootstrap is byte-identical to 036, account launcher byte-identical to 035, normal retry replaces the incompatible pre-launch gate, private namespace and original sandbox argv remain, and 90/210-second budgets plus strict SSH and enabled/active timer guards remain. Build evidence does not establish genuine desktop pixels. New numbered target evidence is pending.

## Installation and launch

Installation preserved all 138 pre-existing EFI hashes. Both non-PID1 guards refused with exit 77; free EFI space was 215,060,480 bytes. Default Ubuntu boot, manual entry and enabled/active screen-off state were preserved. The 1,071,380-byte increment SHA256 is f057e4b0896e721058d9d801af5ce9286266983235365fda4632d4754ae3a248 and its ordered extraction matches the full archive. Installation selected no one-shot entry and requested no reboot.

The separate single diagnostic started 2026-11-14 10:49:40 Asia/Shanghai, from boot 8bd1eac7-21ba-43cf-ad1e-ad437fe49457. Evidence and return verification remain pending below.

## Actual result (closed)

The single run returned to standard Ubuntu at 10:52:32 Asia/Shanghai. All 59 retrieved files matched remote hashes, using read-only noload retrieval without evidence filesystem journal replay. Configured target termination was observed. Original SceneBoard installed and ran; no ENOSPC, failed application seccomp or Mali-context failure was observed by the existing scoped analysis.

The normal Ability Manager request at guest 39.596305 seconds returned CLI status 0 at 39.750251 seconds, followed by real process observation at 41.793626 seconds. SceneBoard logged onCreate at 40.758 seconds; foundation published WMS SA 4606 at 42.913 seconds. This corrects 036's launch regression without modifying original security checks. It does not prove desktop pixels or establish why the reference pre-launch gate is unsuitable in every internal detail.

Three actual 160×256 PPM exports are black. All 16 bounded GL framebuffer observations report complete buffers, nine attempted/nine confirmed RGBA readbacks and zero sampled nonblack pixels. Four deduplicated actual composer records show black client input and completed output, latest at 73.269323 seconds. SceneBoard's first ArkUI first-frame-message flush appears later, at 79.934 seconds. There is no verified post-flush presented frame in this evidence; neither successful eventual desktop nor post-flush black output is established. No further blit/GL dispatch hypothesis is supported by this run.

The original broker still fails seven times with EINVAL setting undefined context u:r:anco_service_broker:s0. The reference namespace does not repair this matching-policy dependency. Next work should instrument bounded post-launch application transaction/RenderService presentation evidence and/or locate the authentic matching broker policy; it must preserve original permissions, identities, sandbox and target policy support. Avoid another early-only black-pixel probe or extending diagnostic timeouts as a substitute for locating the real boundary.

Return verification confirms boot baf07aad-4313-43ea-a4eb-b406ad5abd6f, standard Ubuntu current/default, unchanged firmware/manual entry and all four original images, unmounted evidence partition and enabled/active screen-off timer. Of 138 prior EFI files, 137 are unchanged; only the boot-managed random seed rotated. Actual HarmonyOS audit records show permissive=1; SELinux support/policy/audit are retained. All 037 operational steps are now closed. Never replay them or overwrite their numbered logs.

`commercial61-native-037/presentation-timing-audit.json` preserves source hashes and the exact launch, WMS, readback, frame, broker and first-flush records. No desktop success is claimed.
