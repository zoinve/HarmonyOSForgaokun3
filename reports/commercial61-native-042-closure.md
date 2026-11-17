# Commercial 042 closure and handoff audit

The takeover recovered the already completed 042 run. No boot was repeated,
no new boot entry was installed, and historical reports remain unchanged.
The single original run was 2026-11-14 12:03:34 to 12:07:16 Asia/Shanghai.
The device remains on Ubuntu boot 662a1156-2ca6-4848-b747-91803df33400.

## Runtime result

All 63 files in runtime-evidence matched their remote SHA256 values.
Retrieval mounted the evidence partition read-only with noload and unmounted it.
The configured target termination and final diagnostic exit were observed.
Original SceneBoard installed and ran. All seven physical scanout exports are
black. Desktop and physical input acceptance remain false.

The original transaction observer captured 296 records across the parent and
three real applications. SceneBoard PID 3745, UID 20020025, called the original
SetRSRootNode with a nonnull root. Original GetUniRenderEnabled returned 1;
GetHybridRenderEnabled returned 0. Ten sampled proxy flushes entered and
returned. Sampled nonempty queues became empty and the public transaction
index reached 34 at guest 120.008 seconds. These observations exclude an
always-empty UI queue or a missing root as explanations for this run. They
do not prove delivery of all transactions or presentation by RenderService.

No client_commit/rpc_commit observation was captured. This is NOT proof of
failed submission. A new read-only audit of the exact commercial system image
found SYMBOLIC binding in librender_service_base.z.so, direct intra-library
calls, and indirect virtual dispatch in the actual transaction path. These
paths need not pass through the preload's same-named symbol definitions.
The original CommitTransaction implementation sends RPC code 0; application
agent registration sends code 17. Request codes alone do not identify a
remote service and must not be used as delivery proof without endpoint evidence.

The original service also logged creation/registration of SceneBoard
surfaces and later offscreen capture requests. Thus the entire app-to-RS
connection cannot be classified as absent. Missing-application-agent warnings
remain relevant, but their cause and relation to the absent final frame are
unresolved. No speculative root injection, fake response, forced OOBE state,
identity substitution, or authentication bypass was introduced.

## Preservation

Post-return verification confirms standard Ubuntu current/default, unchanged
firmware, all four original image hashes, retained original manual boot entry,
unmounted lab partition, and enabled/active screen-off timer. All 101 remaining
prior EFI files were unchanged; the normal random seed changed. The authorized
hash-matched removal of commercial 040 is accounted for separately. Latest
experimental entries remain 041 and 042; shared payloads were not removed.
HarmonyOS retains SELinux support and permissive-mode diagnostics, not disabled
SELinux; Ubuntu security configuration was not changed.

## Next integration boundary

Do not replay 042 or extend the timeout as a remedy. The next candidate must
observe actual transaction delivery and original RenderService scheduling,
without relying on preempting its internally bound methods. Any Binder-level
observation must validate the matching public UAPI, identify the real endpoint,
preserve request bytes, results, errno and identities, and distinguish accepted
requests from final render/present success. Complete library-map reads are
needed before any duplicated-runtime diagnosis; historical one-read maps were
potentially truncated. No new candidate is installed by this audit.

Keep all three pinned references: HarmonyMac's original service/NativeWindow
integration, L410 HarmonyOS Adaptations' private graphics namespace, and L410
Linux Compatibility Platform's later AnCo integration. The latter is not a
replacement for the original desktop. The main acceptance criterion remains
real original desktop pixels and interaction, not a private-function microtest.

New static evidence is in reports/commercial-transaction-audit-043; the original
042 runtime and preservation JSON files are in reports/commercial61-native-042.
