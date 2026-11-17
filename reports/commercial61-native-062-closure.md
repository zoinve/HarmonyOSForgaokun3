# Commercial native 062 closure

## Result

One bounded boot ran 2026-11-14T17:56:34.433531Z to
2026-11-14T18:00:16.365869Z, returning to Ubuntu boot
11ae3ed7-0c17-49df-be00-2718e019c441. Run:
commercial61-native-062-8f0a8388-8ba3-4652-a3d9-c8c79649f59d.
64 retrieved evidence files matched remote hashes with read-only/no-replay
access. Configured timeout/exit 9 and stopped observer were recorded.
Seven sparse captures remain black. Desktop and interaction are not achieved.

## Account Retry Reached Original Service And Was Denied

The original default activation failed before SceneBoard readiness again:
44.725s scb does not exist; 44.728s OnStartUserDone reports error 22;
44.752s SendToAMSAccountStart fails and account activation rolls back.
Original WMS-ready write follows at 46.792s.

Original acm process PID 4096 appears at 47.498s. At 47.501s accountmgr logs:
ActivateOsAccount, os_account_manager_service.cpp:1125, permission denied.
The supported CLI route reached the genuine service but did not activate the
account. The native permission check remains intact. No identity, token or
permission policy was changed to make the request succeed.

No successful account callback or account-ready write was found. Animation
finished was written at 73.009s; BootAnimationNode drawing continued to 120.020s.
No boot-completed/release success is established. Log absence is not full
execution coverage, and missing HDF-ready observation remains a separate gate.

account-analysis.json initially found no diagnostic kmsg markers; it must not
be used to claim the CLI did not execute. account-analysis-revision2.json adds
the direct original acm and permission-denial logs. Both artifacts are retained.
CLI exit status was not captured. Subsequent diagnostic should retain a bounded
script log as a file and read it through the existing outer stream helper.

## Graphics And Observation

188 attachments; zero failures, perf losses, malformed records or IP mismatches.
2872 sample log records were suppressed. Logged events: AddChild 384,
AttachToUniSurfaceNode 2, UpdateModifierNGDrawCmdList 286, UpdateRecording 41.
Observer specifications are exactly the audited 061 original handlers; only
diagnostic experiment labels changed. No new private-state observation.

SceneBoard first flush: 81.316s. Three subsequent composer frames, last
120.060521s; zero sampled nonblack post-flush frames. Public full-render mode
from 059 remains. The account CLI denial leaves the earlier lifecycle failure
unresolved; no new EGL/composer workaround was installed.

## Build And Preservation

Exact archive delta from 061: init and native-target/desktop-order020.sh.
Delta from 045 additionally includes the single-line board full-render parameter.
Original service binaries, modules and bootstrap are byte-identical to 045.
Original security/identity checks and OOBE state are unchanged.
Six shell-flow tests, synthetic ring/memory tests, exact archive comparison,
workflow guards and ordered overlay equality passed before installation.

Init SHA256: 7833c656de9f7d4a181e0e404a48fec6e5001fe0235c37e73b0fa3e914f6f880.
Full initrd: d38ccd4df771ae8dc398bc53193cfa51cace824d72db7f8d1150c281530a22d0.
Installed overlay: 0aadfc18d0ad7ef3b4a1e86d71a50b294cda519d9824890a31aceb083caab45b.

Full return verifier passed: Ubuntu current/default, original manual entry,
firmware, four original image hashes and enabled/active screen-off timer.
Lab partition is unmounted. 124 prior EFI files matched; random-seed is the
normal managed change. Retention 20261114T175625511803Z hash-archived/removed
entry 060 before boot. Entries 061/062 and shared payloads remain.

## Next Integration Boundary

Do not impersonate an authorized acm caller or relax its permission check.
Inspect a bounded original-init accountmgr restart after SceneBoard/WMS is
ready, using the existing begetctl lifecycle mechanism and original service
configuration/token assignment. Verify original default activation actually
retries, callback succeeds and remaining boot events complete. Do not infer
success from service restart, PID presence or CLI exit alone. Do not repeat 062.
