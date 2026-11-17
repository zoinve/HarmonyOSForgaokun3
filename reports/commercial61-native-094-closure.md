# Commercial 094: user-interrupted OOBE run

## Outcome

The user reports reaching OOBE and then forcibly rebooting. This is not a
verified automatic return, native desktop success, or native startup failure.
094 was booted once and must not be repeated.

The read-only partial audit located run
`commercial61-native-087-03ee3956-2e72-4b97-a788-dd8e7d754bfd`.
The latest preserved cumulative log is `phase-116.log` (7,723,840 bytes).
The late desktop diagnostic file required by normal retrieval is absent.
Raw evidence remains on the target, unmodified; only file metadata and
sanitized selected markers/frames were exported.

## Independent Runtime Finding

Before interruption, SceneBoard PID 4418 reported `THREAD_BLOCK_3S` at
2026-11-15 16:47:01 target log time. Its recorded event file is
`THREAD_BLOCK_3S-4418-20261115164702.log`, 270,176 bytes.
The first recorded stack follows:

1. `std::__h::condition_variable::wait`
2. `std::__h::__assoc_sub_state::wait`
3. `libcollabfwk_devicedetect_client.z.so`
4. `libcfwk_devicepicker_client.z.so`
5. `NapiDevicePickerManager::Js_GetTrustedDeviceListSync`

This reproduces the native waiting chain observed in 092. It does not establish
that missing identity alone caused the wait, nor that the subsequent user reboot
was an automatic watchdog action. Early identity markers and original UDID API
success are not established by these partial exports.

## Evidence And Preservation

- `commercial61-native-094/interrupted-run-audit.json`: initial inventory.
- `commercial61-native-094/interrupted-run-focused-audit.json`: event markers.
- `commercial61-native-094/interrupted-run-stack-audit.json`: first stack filter;
  process metadata filled its bounded selection, so it is not the stack basis.
- `commercial61-native-094/interrupted-run-stack-audit-v2.json`: narrowed frames.
- `verify-commercial-return` passed after initial audit: Ubuntu current/default,
  154 prior EFI files unchanged except normal loader random seed, original images
  and firmware unchanged, LAB unmounted, screen-off timer enabled/active, original
  manual entry retained.

## Next Investigation

Investigate the original device-detection service and IPC response associated
with the synchronous devicepicker call. Keep normal lifecycle/authentication
checks; do not replace trusted-device results or fabricate identity/provisioning.
A new numbered run must collect identity status before the late desktop phase,
and complete bounded evidence capture without manual interruption.
