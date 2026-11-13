# Experiment 916: normal desktop commands did not stop the guide

- Native ARM/KVM, existing VirGL graphics, headless, normal user networking.
- The UID/GID 2000 shell had zero effective capabilities. Both normal `aa start` and `aa force-stop` printed failure, despite returning exit status 0.
- The guide retained PID 6691 across both calls and three later observations: termination did not occur.
- The independent UID 0 comparison produced the same command failures. Its shell regained effective capabilities on exec (`000001ffffffffff`), so it is **not** a zero-capability comparison. No foreign service token or identity was borrowed.
- Read-only persisted-log extraction exposed the CLI failure messages, but not the underlying client error code.
- No activation, identity, trust, or readiness state was edited. No desktop is verified.

The next immutable diagnostic payload (917) removes the root comparison. A preload library is scoped only to the two ordinary-shell `aa` commands. It forwards the original client calls and arguments, records the actual return values and target libraries, and returns those values unchanged. It neither grants permissions nor substitutes successful responses.

Payload 917 SHA-256: `02fea19c7f3de4b1282a7c0e43665e1bb4191c152c509b62666ed28b2f67781c`.
Actual archive executable-mode check passed. Experiment 916 subsequently exited with code 0; all original-image integrity checks passed. Its independent userdata was deleted after verifying no QEMU/open descriptor and checking the protected original userdata hash before and after deletion (`userdata-cleanup-916.json`). Experiment 917 is running; its runtime result is not yet known.
