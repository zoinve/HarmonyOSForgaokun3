# Commercial 045 closure

The single boot ran 2026-11-14 20:22:52 through 20:26:34 Asia/Shanghai,
returning to Ubuntu boot e1f179c8-ef85-4113-b27d-fbcf58902011. All 63 raw
evidence files match remote hashes. The target timeout was observed. All seven
sampled scanout exports are black. Desktop and interaction remain unverified.

The independent kernel uses authentic held sender TGID references translated
into the receiver PID namespace for incoming oneway sender_pid. Userland is
unchanged from 044. The prior missing-application-agent warning is absent;
this is not direct observation of the registered PID. Original RS logs show
SCBDesktop and wallpaper nodes on the tree. SceneBoard sends real code-17 and
code-0 transactions to the original RS endpoint with full kernel consumption.

Hash-checked render-analysis.json shows the first SceneBoard ArkUI flush at
guest 78.800 seconds, while the last composer frame is at 74.535110 seconds.
There are zero observed post-flush composer frames. At 79.114178 and 120.012965
seconds original SceneBoard still sends code 0. Sampled main RS threads wait
in epoll and render threads in futex. Waiting is not proof of deadlock; kernel
acceptance is not proof of service execution. Early GL readbacks cannot
diagnose these absent post-flush frames. Original internal method binding
also means absent preload logs do not prove methods did not execute.

Post-return verification confirms original image hashes and firmware unchanged,
Ubuntu current/default preserved, original manual entry retained, evidence
partition unmounted, and Ubuntu screen-off timer enabled/active. There are 105
unchanged prior EFI files, the normal random-seed update, and the hash-matched
authorized removal of entry 043. Latest experiment entries are 044 and 045.
Target SELinux support and permissive mode remain, not disabled SELinux.
No identity, token, authentication or sandbox bypass was introduced.

Next observe actual original RS receive/unmarshal/cache/frame scheduling using
target-only tracing. Kernel 045 has PERF_EVENTS but no FTRACE or KPROBES;
this requires an independent numbered kernel, not changes to Ubuntu or 045.
Do not repeat this completed boot.
