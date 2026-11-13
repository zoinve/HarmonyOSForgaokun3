# Headless command evidence (873)

- Native ARM/KVM, unchanged kernel 823, fresh independent userdata, no viewer.
- `LAB873_SHELL_ENTER` proves shell execution as UID/GID 2000,
  `u:r:sh:s0`, `CapEff=0`; no service identity or token was borrowed.
- `aa start` prints `error: failed to start ability.` but exits 0.
- `aa force-stop` prints `error: failed to force stop process.` but exits 0.
  Neither operation is verified successful. Future checks must inspect command
  output and actual process/UI state, not exit status alone.
- Process snapshot: SceneBoard PID 5275, OOBE PID 5919, render_service PID 1314,
  foundation PID 1258. Presence does not demonstrate a responsive desktop.
- `access_token_id ... magic fail, TYPE=84` occurs near aa calls. The reference
  OpenHarmony driver declares ioctl base `A` (65); an ABI mismatch is a lead,
  not yet established as the cause. No permissions or authentication changes.
- `hilog -x -d` is invalid here (`d` requires an argument). It produced no
  useful application log despite a pipeline exit status of 0.
- `command-probe-final.png` shows a black page with a blue OOBE next arrow,
  not a desktop. No desktop success claim.

Next isolated experiment 874: send SIGTERM once only to an exact full OOBE
cmdline match, within the user's existing runtime OOBE termination permission;
preserve SceneBoard, critical services and watchdogs. Capture subsequent UI
and collect actual hilog help/output. No activation/readiness edits.
