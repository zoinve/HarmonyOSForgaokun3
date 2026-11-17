# Original device-detection query: delayed, not permanently stuck

This is an offline analysis of preserved 092 evidence, not a new boot experiment.
Source archive SHA-256 and sanitized matching lines are recorded in
`original-devicedetect-095.json`. Original evidence is unchanged.

## Observed Sequence

All November timestamps below are target log time on 2026-11-15. Startup logs
also contain January timestamps; do not treat those as wall-clock duration.

- Original DeviceDetect service PID 906 logs `publish success` during startup.
- 16:12:01.000: SceneBoard PID 4303 enters the trusted-device filtered query.
- 16:12:01.001: its asynchronous worker PID/TID 4303/7427 enters the inner call.
- 16:12:02.001: the main-thread proxy reports an inner-call timeout and `leave`.
  This log alone does not prove the JS call returned: later frames still show
  the original future/condition-variable wait.
- 16:12:08.516: original service worker 906/1466 logs query stage 1.
- 16:12:10.930: original device manager returns success with zero trusted devices.
- 16:12:10.933: original SceneBoard NAPI reports `return 0 devices, ret: 0`.
- 16:12:10.934: SceneBoard logs `Find 0 device` and continues component lifecycle
  at 16:12:10.939.

The query spans approximately 9.933 seconds. The evidence contradicts a claim
that this 092 query never returns, that no device-detection service was published,
or that a fabricated trusted-device response is needed. A 3-second freeze frame
is a sample of the delay, not proof of a permanent deadlock.

## Remaining Leads

Service logs show BluetoothHost SA 1130 removal/addition, `seviced not all ready`,
and missing local network info around the query interval. These are correlations,
not established causes. Local-device lookup later reports ret 0. No authentication
denial or sole identity root cause is established by this sequence.

Continue correlating SceneBoard/OOBE lifecycle and rendered frames after the
successful native return. Future diagnostics should capture early identity status
and the query's eventual completion before the late desktop snapshot; do not
modify original service results, authentication, or watchdog behavior.
