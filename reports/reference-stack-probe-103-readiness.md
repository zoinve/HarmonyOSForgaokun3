# Reference stack probe 103 readiness

This is a probe build and local loading check, not a boot experiment or desktop
acceptance. Target services and original images were not changed.

## Why a new observation is needed

The complete SceneBoard appfreeze snapshot in 101 explicitly says
`PeerBinder pids is empty` at decoded line 814. Its accepted snapshot inventory
contains SceneBoard and caas_service faults, but no CollaborationFwk fault.
Client Binder waiting is established; a server native waiting stack is missing.

The image's command-line /system/bin/dumpcatcher is a 4376-byte executable whose
only diagnostic message is `dumpcatcher is supported only in the root version.`
Do not assume this CLI implements stack collection or replace its security
checks. /system/bin/processdump is an internal request-driven backend, not a
verified equivalent PID-oriented CLI.

## Reference implementation reused

HarmonyMac revision f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad already provides
ports/tests/app-stack-probe.cpp and its DFX header. Both were copied byte for
byte, including header attribution. The probe calls the original
DfxDumpCatcher::DumpCatchWithTimeout with an 8000 ms timeout and a 20-second
alarm; the `all` argument selects all target threads.

The probe links the supplied image's original libdfx_dumpcatcher.z.so, libc++.so
and libc.so. All 19 libraries in the extracted dependency graph have recorded
image paths and hashes. SDK headers/compiler support are used, not SDK shared
runtime replacements. Binary SHA256:
bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181.

## Verification and remaining gates

The original native loader loaded the probe and libraries under qemu-aarch64.
All five invalid PID cases returned 2 as the unchanged reference source requires.
HiLog socket warnings are expected in this local loading environment. No DFX
dump request was made. See reference-stack-probe-103/load-tests.json.

Target permission checks, DFX server operation and successful stack collection
remain UNVERIFIED. Local loading must not be represented as successful capture.

A future independently numbered observation must retain all original startup,
identity, network, authentication and recovery behavior. Collect CollaborationFwk
native stacks during the first SceneBoard query, with bounded commands and a
dedicated independently retrieved log. Record observer timing/perturbation and
failed/partial captures. Do not append to the non-append-owned 101 diagnostic
stream, infer desktop from an API success, or rerun completed 101.

Before any new boot, integrate and test the new log's export/retrieval path,
existing isolation/admission guards and full preservation workflow. The probe
alone is not boot admission. The full native desktop goal remains active.
