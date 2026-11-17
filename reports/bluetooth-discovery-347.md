# Bluetooth Discovery341

Date:2026-11-17, Asia/Shanghai. This turn made progress: new original-service
and actual-controller evidence, not a repeated status-only turn.

341 ran once and returned automatically to Ubuntu at2026-11-16T19:10:33Z
(2026-11-17 03:10:33 Asia/Shanghai). Run:
commercial61-native-087-1ea47b26-bdf8-45b3-9f3e-39f8d98bbc8e.
Collector343 retrieved19 files. Do not repeat341. Future retrieval exclusions
must include341 alongside235,253,262,266,276,285,294,297,306,321,331.

## Actual BLE Scanning

Original Bluetooth service enabled successfully and recorded switch-on again.
Original service logs show7 StartScan requests. The real QCA broker, without
translating commands/events, observed three LE extended scan-enable requests
and two disable requests (opcode2042). All five real Command Complete events
reported status0. phase-181.log166738-166747 contains these transactions.

The observer recorded at least2624 structurally valid LE advertising report
packets; latest counter is at phase-181.log339053. It validates H4 event length,
record count and record/data lengths before counting. Reports may repeatedly
describe the same device; this is NOT2624 devices and does not prove that
Settings displays a nearby list or that app-specific filters deliver results.
No nearby names/addresses were added to the observer output. Original data
is forwarded unchanged; no synthetic advertisement or scan completion exists.

Tests344 used local fixtures only and passed address/undefined sanitizers:
scan request/status classification, rejected command status, valid LE legacy
and extended reports, Classic report structure, truncated/invalid lengths.
Build341 also compiled the integrated namespace launcher and ARM64 broker.
See commercial61-native-341/bluetooth-analysis-346.json.

## Original UI Launch Refused

Original image Settings metadata declares BluetoothSettingsAbility in pc_settings,
action.settings.bluetooth, with ACCESS_SYSTEM_SETTINGS permission.339 requested
that exact ability through original aa, with unchanged UID/GID, verified target
root/net/mount/PID namespaces, and an8-second subprocess bound. No token was set.

The original command printed Error Code10108101 and failed to start ability,
although its Unix exit status was0. Do NOT treat that process exit as success.
Hilog122537-122543 identifies invalid TokenID, dominate-screen caller invalid,
and StartAbilityError:-1; launcher result2097205 maps to10108101. This is a
rejection of an external diagnostic caller, not proof that the already-working
user Settings app is broken. Do not resume Settings recovery or retry this
same unauthenticated aa launch. Do not forge/borrow a service/app token, alter
the permission policy, or relabel BLE system-component scans as UI scans.

No Classic inquiry command was observed, and no pairing/reconnection was
attempted. Nearby-device UI, deliberate peer pairing and low-power acceptance
remain pending. A legitimate user/app path is required for their next test.

## Other Drivers And Preservation

Audio retained real PCM playback:360960 submitted frames, stream-end result0.
Acoustic output remains unverified. Audio broker exited normally:forced0/status0.
Touch observer exited normally with0 frames/0 concurrent contacts/0 drops;
physical multitouch and app gestures remain pending.120Hz unchanged.

Entries173/341 are retained.331 entry was archived before retirement. Cleanup345
removed only unreferenced set321.img (3227963 bytes), leaving all active boot
dependencies, data165/197, original images, Ubuntu default and enabled/active
screen-off timer intact. No disk hash/fsck/tree-validation suite was rerun.

Next useful work is real driver functionality and scoped acceptance, not more
root-aa launch experiments. Preserve working BT/audio integration in new builds.
