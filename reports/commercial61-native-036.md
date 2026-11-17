# Commercial 036 — reference service startup and appspawn namespace

Continues closed 035 without replaying any historical operational diagnostic. Genuine original desktop pixels remain unverified. The prior last black scanout preceded SceneBoard's first-flush log; that log alone does not prove RenderService received or presented content.

This candidate integrates the pinned HarmonyMac public SAMgr probe, byte-identical source linked against extracted original commercial runtime libraries, and its SceneBoard readiness gate for SA 401, 501, 4606, 4607. An extra final probe fails closed after the bounded reference wait. It preserves normal Ability Manager launch and omits the reference's guide force-stop, unconditional READY marker and denied dump request.

The pinned L410 appspawn namespace main is retained unchanged: private mount namespace, private provider bind, removal of LD_LIBRARY_PATH, and exec of the original appspawn with its complete original sandbox argv. Only the preload list changes to the original appspawn helper; Kirin/Mali/OOBE compatibility shims are omitted. The provider remains this board's existing backend. This does not replace original appspawn or change service identity, policy, authentication or permission gates.

L410 Linux Compatibility Platform remains the reference for subsequent Wayland/XWayland/AnCo application integration. Its README explicitly excludes service startup/deployment scripts; it cannot substitute for successful original service/RenderService/desktop integration. All three references are used within their actual scope.

Offline reference gate, namespace and native integration checks passed. The gate test covers ready and timeout branches; namespace main is reference-identical and sandbox argv retained. Full candidate build succeeded. The 1,071,186-byte increment (SHA256 c2c24891096b67558bd69d6d6c78aa50ec9a5cadc8bf6fe814f8f9e11b20a6d0) reproduces full archive bytes and modes when extracted after the existing 001, 017 and 016 layers, with required parent ordering verified. Target/outer deadlines remain 90/210 seconds. A 120-iteration readiness wait cannot extend those outer guards; an unavailable dependency may consume the remaining target budget without launching SceneBoard.

New workflow files explicitly require strict trusted host-key checking, batch authentication and per-command 192.168.10.128 address/alias. Existing Windows SSH identity/configuration is used through a temporary local invocation adapter, without global SSH changes. Ubuntu screen-off enabled/active, default boot, original images, EFI reserve, memory admission, non-PID1 refusal and exclusive evidence creation remain required. SELinux permissive is authorized for HarmonyOS; actual target mode must be read from evidence.

Deployment and target result are recorded below only after completion. Build evidence is not target or desktop proof.

## Installation and single launch

Installation preserved all 136 pre-existing EFI hashes and unchanged firmware/default/manual entries. Both non-PID1 guards refused with exit 77. EFI free space is 216,141,824 bytes. The screen-off timer was enabled/active. Installation itself selected no one-shot and requested no reboot.

A separate single guarded diagnostic started at 2026-11-14 10:41:41 Asia/Shanghai (02:41:41 UTC), from Ubuntu boot ae587799-0092-448b-9f44-6d8822c91e71. Its exclusive boot-attempt record prohibits replay. Runtime result is pending retrieval.

## Actual result (closed)

The single diagnostic returned to standard Ubuntu at 10:44:08 Asia/Shanghai. All 59 retrieved files matched remote hashes; read-only noload retrieval did not replay the evidence filesystem journal. Configured target termination was observed (`COMMERCIAL036_TARGET_EXIT pid=308 status=9`). Three valid 160×256 PPM exports are black. SceneBoard installation succeeded, but its process and first-frame log were not observed. This is a startup regression relative to 035, not desktop success or a test of post-launch SceneBoard drawing under the new namespace.

The new reference gate began probing around guest 38.985 seconds and never progressed to SceneBoard launch within the target budget. SAMgr itself reports `NF SA:4606,3151_1` for the first probe; no WMS publish record appears in 036. In sealed 035, SceneBoard `onCreate start` is logged at 40.727 seconds, followed by foundation's `Publish SA:4606 result:0` at 44.487 seconds. This supports a commercial startup-order incompatibility with requiring WMS before launch; it does not by itself prove every internal dependency. Probe access-token errors are also recorded. SELinux SAMgr checks explicitly say permissive=1, so those AVC lines alone are not an enforcing denial. No security check was removed or identity fabricated.

The original broker's undefined `anco_service_broker` context failure still occurs. Changing the namespace did not repair it. The static L410 wrapper reached original appspawn, but without SceneBoard execution this run cannot establish its impact on application rendering. The next candidate should retain the reference namespace and restore the previously exercised normal Ability Manager launch/retry order, treating WMS availability as a post-launch observation, not a pre-launch gate. Do not extend the startup timeout to hide this regression and do not replay 036.

Return verification confirms Ubuntu boot 8bd1eac7-21ba-43cf-ad1e-ad437fe49457, standard current/default entry, unchanged firmware/manual entry and all four original image hashes, unmounted evidence partition, and enabled/active screen-off timer. Of 136 prior EFI files, 135 are unchanged; the legitimate boot-managed random seed rotated. An initial read-only verification overlapped the temporary evidence mount and refused; after retrieval unmounted it, sequential verification passed. No diagnostic was repeated. Actual HarmonyOS SELinux audit records show permissive=1 with policy/audit retained.

Raw-derived comparison is preserved in `commercial61-native-036/reference-start-order-audit.json`. All 036 operational steps are closed and immutable.
