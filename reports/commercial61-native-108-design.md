# Original Memory-Wrapper Prerequisites 108

107 captured the real query waiting in the DeviceManager SDK mutex. DeviceManager
registration threads wait on the memory client's mutex and an SA 1909 lookup;
the original memory-service namespace wrapper is a zombie. Its static main
requires a bind source at /data/local/tmp/memmgr-nohyperhold-v1/memcg and a target
at /dev/memcg, but does not create them. Its actual failure errno is still unknown.

108 records pre-init lstat results and creates only missing directory scaffolding
for those existing wrapper paths. It refuses non-directory objects and symlinks,
retains existing metadata and contents, and does not create memory metric files.
The /data filesystem is the existing disposable RAM-backed ext4, initialized
before this helper. /dev is the private target tmpfs, never Ubuntu's /dev.

Original init retains control over memmgrservice startup, identity/token checks,
permissions, binary code, original namespace wrapper and all recovery/watchdogs.
No service success or setup completion is fabricated. The helper does not itself
mount a replacement hierarchy; the supplied wrapper follows its existing code.
The prior query-event observer and genuine reference DFX probe remain unchanged.
A passive monitor records original SA 1909 checks and fixed public service keys.

The changed runtime must be loaded from the actual 108 path with both SHA256
checks updated. The 107 path inheritance detail is not carried into this changed
runtime. Archive changes are limited to outer init, its tracked wrapper hash,
and the added passive monitor. No original image, kernel or firmware is changed.

Admission verifies exact source and archive deltas, six real-C helper tests,
unchanged event observer, three QEMU isolation guards returning 77, full ordered
overlay equality, and inherited one-boot/privacy/preservation gates. Install
only once after admission, archive entry 105 before retention cleanup, and keep
107/108 plus Ubuntu/default/manual and shared payloads. Retrieval remains noload.

Measure genuine SA 1909 publication, service lifetime, actual query duration,
SceneBoard watchdog stability, full-resolution frames and visible interaction.
If SA 1909 remains absent, inspect original wrapper and service errors rather
than presume the directory hypothesis succeeded. This change alone does not
establish persistent OOBE dismissal or a stable interactive desktop.
