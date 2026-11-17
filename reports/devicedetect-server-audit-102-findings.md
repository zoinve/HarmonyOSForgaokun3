# DeviceDetect server audit 102

Read-only analysis of completed 101 evidence and libraries extracted from the
supplied system image. No new target boot, service changes or image writes.

## Correlated server timing

Both original queries reached CollaborationFwk PID 930, TID 1455. The first
request took 10724 ms from reading its filter list to stage 1, then 2305 ms to
reply (13029 ms server interval). The replacement SceneBoard query took 7 ms
and 4 ms respectively (11 ms server interval). Full client duration additionally
includes IPC and dispatch time. Source hash and exact lines are preserved in
devicedetect-server-audit-102.json; parser/attribution tests passed 3/3.

This establishes that the service was present and narrows most of the first
delay to the pre-stage-1 interval. It does not identify the blocking instruction
or prove which initialization event caused the delay. The later query occurs
after original watchdog recovery, so it is not a controlled intervention.

## Important interpretation correction

The literal log `localDeviceInfo is nullptr 0` means the pointer is NOT null.
The binary compares the pointer with zero at 0x41ec0, uses `cset w8, eq` at
0x41ec8 and passes that boolean to logging. A logged zero means false.
It does not prove a populated network ID, but must not be called a null pointer
failure. Null-related keys in the initial JSON denote matching literal text;
this report and static analysis supersede any implied null-pointer diagnosis.
The original generated JSON is retained unchanged.

## Static boundary

The supplied profile configures SA 70635 with the image's L410 local-policy-v1
DeviceDetect service library. This is a baseline image adaptation, not a newly
introduced patch and not evidence of a HarmonyMac difference.

The service query entry calls GetLocalDeviceUdid, GetLocalDeviceNetworkId and
GetLocalDeviceType before emitting stage 1. Local-info readers use shared/exclusive
locking and the original DeviceManager update path. Bounded disassembly, binary
hashes and boolean assertions are in devicedetect-server-static-102/analysis.json.
No binary was patched, no result fabricated and no security checks removed.

Next evidence needed: a server-side native wait stack in this first-query
interval, or equivalent original IPC timing that identifies the blocking call.
Do not assume missing network, activation or identity is the cause. Do not
repeat 101 or schedule an arbitrary kill-delay variant. Desktop remains unproven.
