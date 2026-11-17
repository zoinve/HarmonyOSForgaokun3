# Native 075: Reference Guide Dismissal

User direction: the device now shows OOBE and cannot finish the network step;
use the supplied HarmonyMac development desktop path.

Pinned reference: HarmonyMac `f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad`,
`ports/tests/native-desktop-start.sh`. Its real commands start SceneBoard and
force-stop `com.huawei.hmos.hwstartupguide` after the real process is observed
and a ten-second wait. It does not complete commercial activation. The earlier
assumption that all guide dismissal was prohibited was too broad for the user's
current request. No activated identity, provisioning flag or success response is
fabricated in this experiment.

075 uses the same original commands, with a fail-closed wait for all four real
reference services and both SceneBoard and StartupGuide processes. It runs in
the existing diagnostic root context, does not impersonate another service,
and records actual command returns, process observations and public dumps.
Original init service definitions, account-order script, security checks,
installed records, HAPs, resources and image files remain unchanged from 074.

The own composer backend retains the original capture at 120 seconds and adds
one independent read-only source/scanout capture at 140 seconds. The same tested
pixel writer and publication checks are retained. The second directory has the
same original composer UID 3036 and 0700 mode. Both captures preserve real DMA
sync and full resolution; they do not alter composition or substitute pixels.
At monotonic 132 seconds the observer attempts one LEFTMETA down/up sequence
on the exact physical keyboard name, through its real evdev device. Successful
write lengths alone do not prove that SceneBoard handled the event.

Separate bounded prefix exports preserve the own render/allocator traces and
guide command log. They explicitly do not claim EOF for a live append-only
trace. Older mixed trace streams can interleave; 074's standard render and
presentation analyzers failed rather than accepting malformed evidence.
074's early hilog did not cover the full boot, so its absence of codec error
lines is not proof of successful native decode.

Evidence gates: `commercial-desktop-test-075/result.json` exercises the actual
shell control flow using CLI stand-ins (success, absent services, vanished guide,
stop rejection), and checks the exact added composer source. Native admission
checks every archive member against 074, the original read-only mounts, exact
tested script/source/binary hashes and the ordered seven-part overlay chain.
The incremental overlay is 755373 bytes, SHA256
`08b1f75f39b0393d858dc8da8217136201d3adbbc7cd64f8ed6a4f705bef0b6d`.

Preservation: Ubuntu remains current/default; screen-off timer stays
enabled/active. The independent 270-second fallback, target budget and cleanup
bounds are inherited without weakening. Retention archives only obsolete entry
files, retaining 074/075 and all shared payloads plus Ubuntu/manual entries.

Acceptance remains a genuine desktop and an independently verified input
response. OOBE dismissal, process liveness, colored pixels, successful commands
or activation failure alone do not satisfy that goal.
