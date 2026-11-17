# Native server observation 104 closure

## Result and operational bounds

Completed one boot and one read-only noload retrieval. Do not rerun 104 or
overwrite its evidence. No stable interactive desktop was demonstrated.

- Run: commercial61-native-087-05df4592-f3e2-43bd-ba91-0b62bfca5594.
- Boot request: 2026-11-15 15:33:06.318248 UTC.
- Ubuntu return observed: 2026-11-15 15:37:13.263687 UTC.
- Ubuntu boot ID: b36e199f-9cad-4f56-9270-cd181d11d868.
- Final phase 120 records target_timeout=1 and target PID 443 status 9.
- All 133 retrieved files matched remote hashes. Retrieval unmounted normally.

## New evidence and its limit

The unchanged HarmonyMac DFX probe successfully ran against the image's original
libraries on the target. A dedicated independently exported log retained 81
thread stacks and 630 frames for CollaborationFwk PID 928. The native API returned
0 / Reason:success. Log SHA256:
634194b3ba2a40fa9c670d6bca575e41061d1a71d9612d44e5ad7101b9c8c37c.

This proves the original native DFX capture path works, not the query's wait
cause. The query's client interval was 23:34:37.143 to 23:34:47.092 local target
time, duration 9949 ms. Server request TID 5312 took 5166 ms before stage 1 and
4778 ms from stage 1 to reply. DFX snapshot time was 23:34:48.367, 1275 ms after
client return: it missed both the client and server query intervals.

The observer ran a per-thread proc survey before invoking DFX. This was avoidable
pre-capture work. Its individual duration was not instrumented, so do not assign
the entire delay to it. The observed request thread's proc wait was
binder_thread_read; that survey entry has no individual timestamp and cannot be
used as a waiting-interval stack. See server-stack-analysis.json and
server-capture-timing.json for hashed inputs and precise line references.

## Native lifecycle and desktop

Reference aa force-stop reported success. Original SceneBoard PID 4791 executed
the native guide exception recovery callback 4465 ms after the native exception
and relaunched OOBE. Later window samples at 90/110/130/145 seconds retained
SceneBoard 4791, guide 9637 and focused guide window 66. No OOBE completion state
was fabricated, and original recovery was not disabled.

Two full source frames (2560x1600) and their rotated outputs (1600x2560) were
recovered at 120.013461 and 140.005146 seconds. Rotation comparison differed by
zero pixels. Source frames differed by 4721 pixels; both OCR results were empty.
The image-view tool rejected inputs, so no visual inspection is claimed.
The physical keyboard event6 Meta down/up pair reached SceneBoard 4791 at
23:35:46.058/.136; a correlated visible desktop response remains unproven.
READY, API success, pixel changes and keyboard delivery are not acceptance.

## Preservation

Original four image hashes and firmware matched prior records. Ubuntu remained
current/default, the original manual entry remained, and the screen-off timer
was enabled/active. Entry 099 was archived with contents and hash outside ESP
before authorized removal at 20261115T153256467269Z. Experimental entries 101/104
were retained without deleting shared payloads. 157 prior EFI files matched;
other changes were the normal random seed and authorized entry removal.

The exact Wi-Fi credential comparison passed across all 133 files / 396148089
bytes, with no credential exported. Physical serial and original UDID export
guards passed. Genuine original GetDevUdid helper evidence was valid; TEE failure
log lines do not establish activation as a desktop prerequisite.

## Next decision

The service wait's cause remains unproven. Any next capture should invoke the
same original DFX probe before the proc survey and explicitly mark the call's
begin/end times, then prove overlap from original logs. This is not permission
to replay 104; a new numbered candidate must be built and admitted separately.

Also retain the distinction between UI delay and OOBE recovery: fixing the
DevicePicker wait alone has not been shown to prevent the original lifecycle
callback from relaunching the guide. Desktop integration, visible output and
actual interaction remain the acceptance target, not a passing stack probe.
