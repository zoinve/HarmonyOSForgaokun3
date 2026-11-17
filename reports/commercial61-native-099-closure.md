# Native 099: Reference Script Still Triggers Guide Relaunch

Exactly one operational boot, 2026-11-15 10:08:02.171230 to
10:11:43.956539 UTC. Recovered run:
commercial61-native-087-7b228439-61f5-4853-9928-1c5fb94b1391.
Ubuntu returned with boot ID 26a101c3-fa2a-44fc-8061-2b11798e3320.
All 132 files match remote hashes; read-only noload retrieval did not replay
the filesystem journal. Final phase-120.log records target timeout and exit
pid=431/status=9. This was a bounded completed diagnostic, not a user-interrupted
boot. Do not rerun 099 or overwrite its artifacts.

## Reference Execution And Actual Outcome

The user clarified that the supplied image is the reference image. No other
image was downloaded or substituted. The original pinned HarmonyMac script was
used with only its log destination changed, retaining its service-first command
order and one force-stop. 095's Alt+F4 worker was not launched. Original identity,
network, security checks, packages and lifecycle callbacks were unchanged.

The recovered reference log starts at uptime 13.75, reports SceneBoard start
success and force-stop success, then prints its unconditional READY marker at
uptime 66.53. Its immediate WMS dump still lists the old guide window/PID 6323;
that retained window row alone does not prove whether the process is alive.
Original HiLog independently records aa PID 8262 issuing force-stop at
18:09:27.368, original appspawn observing guide PID 6323 exit at 18:09:27.391,
and the aa success result at 18:09:27.395 (target local log time).

At 18:09:43.139, the same SceneBoard PID 4631 logs sessionExceptionCallback is
called and start oobe again. Original appspawn reports new guide PID 8167 at
18:09:43.499. The exception/relaunch is about 15.744 seconds after the stop
success log, not merely the three-second timing seen in 078.

At all four observer samples, uptime 90/110/130/145, SceneBoard remains 4631,
guide PID is 8167, and focus is guide window 72. Thus reference command ordering
on the current genuine-identity stack did not give persistent dismissal.
reference-runtime-analysis.json preserves hashes, the exported reference log,
sample tables and original lifecycle lines. READY is not desktop acceptance.

## A Remaining Integration Difference, Not A Proven Cause

The sealed runtime also contains two SceneBoard start calls: aa PID 4600 uses
/usr/bin/aa at early log time 01-01 08:00:50.016, and aa PID 5059 uses
/system/bin/aa at target log time 18:09:13.074 after the clock update. Do not
subtract these different clock epochs to infer an elapsed time.

launch-path-audit.json inventories the actual scripts delivered in the 099
archive. desktop-order020.sh, SHA256
2956cccec98b78d8d2eabe0cee95c05fab984ea8af9caadadf06f84ea8099b97,
contains the inherited /usr/bin/aa launch. The 099 reference script contains the
other start. The inherited script waits for genuine HUKS/app framework/BMS,
starts SceneBoard, then retries original accountmgr after genuine WMS readiness.
Its recovered stream reports the launch accepted, account service stop/start
results zero and finally bootevent.account.ready true. Repeated copies in the
phase stream are snapshots, not proof of multiple invocations.

099 is therefore a faithful reference script reproduction, not proof of full
runtime startup equivalence. Duplicate launch causality for the OOBE relaunch
is unproven. Do not simply delete the inherited start: completed 036 already
showed that waiting for SA 4606 before SceneBoard prevented local launch, while
035 published 4606 after SceneBoard creation. That startup dependency must be
addressed while retaining genuine account initialization, not by replaying 036,
extending a timeout, faking readiness, disabling recovery or repeating kills.

## Pixels, Input And Privacy

Both complete source captures are 2560x1600; outputs are 1600x2560 with zero
rotation differences. Capture times: 120.020054 and 140.003713 seconds.
Source PPM SHA256 values:

- 120s: 33c82c102cf7295071308244ab467747ebd535c27b207d2156e72091cff5f2cd.
- 140s: abfb624c913118b784395a00b04d0214e94c75ce230f0562c7e8d474a34d5589.

2,524,623 source pixels differ. OCR returns no text for either image; this does
not prove absent OOBE or successful desktop rendering. The image viewer rejected
image inputs, so no direct visual inspection is claimed.

The exact keyboard event6 receives complete 48-byte down/up writes. One matching
80ms physical keyboard pair and the same SceneBoard's PreLogoKeyEvent down/up
records at 18:10:33.693/18:10:33.765 prove framework delivery, not visible desktop
interaction. The 099 analyzer correlates real public event timestamps rather
than the older hardcoded January 1 timestamp filter; old reports remain intact.

Original GetDevUdid still returns zero/64 valid hex bytes before the late helper;
the recovered DCM log has zero GetDevUdidData failure lines. Original DCM TEEC
failures remain (24 matching lines including repeated error chains, not 24
distinct attempts). These are not desktop prerequisites or activation success.
Physical serial and original-UDID export guards passed. Separate secrecy audit
passed 132 files/386,504,928 bytes with no WPA credential exported or found.

## Preservation And Next Boundary

Ubuntu is current/default; firmware and four original image hashes are unchanged,
the screen-off timer is enabled/active, the manual entry remains, and LAB is
unmounted. Prior EFI files are unchanged except normal random-seed rotation and
the hash-archived authorized removal of entry 094. Entries 095/099 remain;
retention archive stamp is 20261115T100753494621Z. Shared payloads are preserved.

The native stable interactive desktop goal is not achieved. Next investigate the
actual original account/Home/WMS startup dependency and its reference adaptation
differences. A shared original image is not the missing input, and another
arbitrary timing variant of force-stop is not justified by this result.
