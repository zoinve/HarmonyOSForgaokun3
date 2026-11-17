# Experiment 089 closure: readiness gate refused the stop

Exactly one operational boot of entry 089, 2026-11-15 07:01:35.249515 to
07:05:20.973706 UTC. The inherited core retains raw prefix 087; the distinct run
is `commercial61-native-087-41b704b4-77b0-4f0b-81df-e72ab468f735`.
All 131 files matched remote sizes/hashes. Historical evidence was not replaced.

## Actual stop outcome

`single-stop-runtime-analysis.json` and the original diagnostic log establish:

- The original diagnostic service ran, but printed DESKTOP089_DOCK_TIMEOUT.
- Zero stop requests and zero aa results were recorded. This is not a successful
  kill followed by relaunch; no kill was attempted in 089.
- At uptime 105.35, SceneBoard PID 9500 and guide PIDs 6503/10025 were present.
- At uptime 130.71, SceneBoard PID 9500 and guide PID 10025 were present.
- Both original UITest attempts timed out (124); no permission check was bypassed.

The gate's probe files are not included in the inherited snapshot exporter.
Consequently the exact per-poll reason no readiness marker was accepted is not
available. Do not infer that absence of its marker means Dock never initialized.

## Original desktop and service evidence

Original SceneBoard PID 4591 read the one-item canonical workspace at 15:03:01.701
and emitted EVENT_SMARTDOCK_INIT_FINISHED at 15:03:01.888 local time.
Its synchronous GetTrustedDeviceListWithAbilityFilter began at 15:03:05.937.
The client logged its internal timeout at 15:03:06.939, but the main thread still
waited in condition_variable, __assoc_sub_state, libcollabfwk_devicedetect_client,
libcfwk_devicepicker_client and Js_GetTrustedDeviceListSync in both freeze stacks.
This suggests the timeout did not release the main-thread wait; the exact C++
future ownership/destructor mechanism has not been proven.

The real CollaborationFwk PID 934 received filters at 15:03:05.947. Its service
stage 1/2 log was delayed until 15:03:16.261, and completion until 15:03:21.072.
Original foundation killed SceneBoard for THREAD_BLOCK_6S at 15:03:22.925.
Replacement SceneBoard PID 9500 registered its root scene at 15:03:24.093.
The replacement's device query completed quickly at 15:03:26.056. Do not patch
private binaries, fake a device list, or disable the original freeze lifecycle.

Complete original captures:

- 3S: 269735 bytes, SHA256
  `58ce0ad856f05d4355c5147e311ee53e37573245be2c3b1434e662066241d09d`.
- 6S: 270290 bytes, SHA256
  `2e053d0ed70197c313caa65c133cd4f4a12f794a395f3b6595971541247777d2`.

## Network and remaining desktop state

Real independent original curl HTTP and HTTPS probes both returned 204/exit 0;
HTTPS verification result was 0. Native DHCP and supplier/default netId 100 were
observed. Guide PID 6503 received net available at 15:03:02.092. Replacement
guide PID 10025 saw hasDefaultNet true but timed out at 15:03:33.752 without a
recorded validation callback. Internet reachability is therefore not equivalent
to correct callback delivery for the restarted guide.

Both full-resolution captures are complete at 2560x1600; neither constitutes
verified desktop interaction. The goal remains incomplete. Credential secrecy
comparison passed on all retrieved bytes.

## Verification and next work

Archive admission confirms exactly one owned text-script delta. Six isolated
shell-flow tests pass, including absent marker, changed PID, multiple PIDs,
absent guide and failed stop without retry. They do not prove native success.

Post-retrieval serial preservation passes: Ubuntu current/default, firmware and
four original image hashes unchanged, 150 baseline EFI files unchanged except
normal random-seed and authorized archived removal of entry 087, lab unmounted,
screen-off enabled/active, manual entry retained. Entries 088/089 remain.

Important historical correction: 078 already proved same-PID SceneBoard can
relaunch a successfully stopped guide through sessionExceptionCallback. Waiting
for Dock/same PID is not a demonstrated persistent-skip fix. Do not run another
force-stop-only experiment. Investigate real CollaborationFwk request latency
and original network callback delivery using service-side evidence. Supported
OOBE completion must remain genuine; no provisioning records were changed.
