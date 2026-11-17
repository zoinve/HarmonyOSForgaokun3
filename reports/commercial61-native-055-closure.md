# Commercial native 055 closure

## Result

The authentic desktop remains unverified and sparse scanout captures remain
black. One bounded boot ran from 2026-11-14T16:15:02.414024Z to
16:18:44.303124Z, returning to Ubuntu boot ID
`8f636ae0-a587-4d42-ac8d-075056599380`. All 64 retrieved files matched their
remote hashes. Retrieval was read-only without original journal replay.

## Original Integration Boundaries

Four hardware execution sites were audited against the pinned original ELFs.
The command callsite is the virtual command Process invocation at base VA
0x5e8958, not merely transaction entry. The screen skip site is the branch at
service VA 0x1945e8 immediately after CheckRenderSkipIfScreenOff; bit zero of
w0 is the original result. No private objects were dereferenced or modified.

| Boundary | Logged samples | Logged after SceneBoard flush | Hardware count |
| --- | ---: | ---: | ---: |
| Actual command execution callsite | 533 | 130 | 23854 |
| Screen-off skip result | 285 | 52 | 309 |
| RSUniRenderThread::Sync entry | 0 | 0 | 0 |
| RSUniRenderThread::Render entry | 281 | 54 | 303 |

All logged command arguments were non-null. All logged screen skip result
bits were zero, including the 52 logged post-flush results. Command events
came from global TID 1162; worker Render events came from TID 1631. There were
196 successful attachments across 49 threads, no attachment failures, malformed
records, or instruction-pointer mismatches.

Important limitation: the high-frequency command probe lost 15047 samples.
Its parsed sample count was 8807, of which only 533 were printed due to the
drain log cap. Total suppressed log records across all events were 8320.
The other three events reported zero lost samples, but their logged records
are still a subset where suppression occurred. Positive samples establish
reaching these instructions, not command success, completed GPU work, or
presentation. Periodic attachment does not cover all thread lifetimes.
Zero standalone Sync samples cannot exclude an inline or alternate handoff.

The first SceneBoard ArkUI flush was at approximately 76.829 guest seconds.
Only four Composer frame records were present, at 11.936720, 14.302270,
14.351425 and 75.018208 seconds; all sampled source/output RGB values were
black. There were no recorded post-flush frames. All seven 160x256 scanout
PPMs were black. These sparse captures are not full-resolution desktop proof.
The configured target timeout/exit 9 and observer shutdown were observed.

## Build And Preservation

The first offline test compiled and ran its synthetic cases, then failed
because the new build wrapper did not expose `outer` when imported. That
wrapper was corrected; its first output and unit directory were retained.
The corrected offline test used separately named importfix outputs and passed
synthetic ring parsing, exact read-only executable comparison, audited sites,
and archive equivalence. The full initrd differs from 045 only in `init`;
original bootstrap/userland and kernel modules remain byte-identical.
Workflow safeguards and ordered overlay equivalence also passed.

Post-return verification passed for 117 prior EFI files, except the normal
boot-managed random seed and the authorized archived removal of entry 053.
Ubuntu current/default, enabled/active screen-off timer, firmware, original
manual entry and four original images were preserved. Shared payloads were
not removed; the lab partition is unmounted. Entries 054/055 are retained.
Retention archive stamp: `20261114T161454146215Z`.

## Next Work

Move the observations downstream and remove the saturated per-command probe.
The pinned service exports these original integration boundaries:

- RSScreenRenderNodeDrawable::OnDraw at VA 0x41f104.
- RSScreenRenderNodeDrawable::RequestFrame at VA 0x423230.
- RSUniRenderProcessor::PostProcess at VA 0x178c04.
- RSUniRenderThread::Render non-null-root path starts at VA 0x1701c8.

Inspect their actual branches and buffer/composer handoff before selecting the
next low-frequency sites. Do not infer a missing handoff from absent standalone
method samples. Continue the original service/EGL/queue/composer route from
the three references, without changing OOBE completion or authentication.

Sources: commercial-render-audit-055/result.json;
commercial61-native-055/{boot-observation.json,hwbreak-analysis.json,
handoff-analysis.json,render-analysis.json,runtime-analysis.json,hwbreak-test.json};
runtime-evidence/retrieval-manifest.json; commercial-return-audit-055/result.json.
