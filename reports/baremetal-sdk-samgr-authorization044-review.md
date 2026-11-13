# SAMGR list authorization investigation 044

## Observed failure versus static explanation

Trial 043 received 96 identical genuine UID-5555 SAMGR replies: `TF_STATUS_CODE`, status `1`. These are rejected requests, not a valid empty ability list. Its original result and independent verification remain unchanged.

Read-only cross-reference analysis of the unchanged original `samgr` identified the list handler at `0x846d8`:

- `0x84718`: obtain the actual calling token through `IPCSkeleton::GetCallingTokenID()`.
- `0x84720–0x84728`: require `AccessTokenKit::GetTokenTypeFlag(token) == 1` before proceeding.
- `0x84970`: the non-native-token path returns `1`, matching the observed transport status.
- Only after the type check does `0x84744–0x84754` obtain the caller SID and call `ServiceChecker::ListServiceCheck`. That check has its own denial path.
- Only after both checks does the handler read the dump flag and produce a status/vector reply.

The original access-token SDK implementation at `0x106b4–0x10774` returns `-1` for token zero, otherwise `(token >> 27) & 3`. This is disassembly evidence, not a newly executed SDK call. Evidence: `baremetal-sdk-samgr-list-xrefs044.json` and `baremetal-sdk-token-type044-complete-audit.json`.

The observer forked before original init assigned native identities. An inherited zero token is therefore a concrete hypothesis for this rejection; the actual observer token still needs measurement. This does not justify copying PID1/SAMGR tokens, bypassing the native-token check, changing a caller domain, or weakening policy.

## Bounded diagnostic 044

Fresh 044 reads only its **own** token with the actual device GET ioctl after a real manager reply. It records the SDK-equivalent type classification without writing identity or permissions. A real error reply is terminal; absent/dead managers remain condition-retried. The test distinguishes these outcomes and passed using compiled native C. The generated init also passed strict host compilation and actual non-PID1 refusal.

Preparation produced a 784,840-byte ARM64 init, SHA-256 `81989444592c915eb3926740ac03e19641acd0b88a66c6cfb7ef2daee197ac99`; source SHA-256 `81d7b5cb158749cb77cd9dc284fe3db12ad954e88b304e6f1272898e7e1f8e8f`.

## Actual result

The original-init QEMU observation completed its 60-second bound. The observer measured its own actual token as **zero**, successful GET ioctl, SDK-equivalent type **-1**. It then received exactly one genuine UID-5555 SAMGR status-1 reply and emitted the terminal-rejection marker with enforcing still `1`. No identity or permissions were changed. Together with the original server's native-type check, this identifies a sufficient reason this pre-boot-forked observer cannot list services. It is not evidence that the Binder/token driver should accept an invented native identity; the separate SID check remains untested for a valid native observer.

Full service readiness and a successfully decoded SA list remain **false**. The bounded runner's `runtime_verified=false` is retained. The original SDK selected its own unchanged developer policy, as in the preceding original-init trials; this must not be confused with the separate production-policy probes.

Serial: 145,873 bytes, SHA-256 `1d39574f175553d6b25d18dda2b35a25c0b434dbebc209efa749e47348e0321e`. All three whole original images, the test kernel/configuration, native configuration, and critical sources remained hash-identical. Only the fresh private scratch filesystem changed. No physical reboot, network, GPU, Ubuntu, or original SDK image changes occurred.

The targeted real-driver host regression also passed all four groups: unsupported commands, identity authorization, permission data, and initialization failure cleanup. Independent 044 verification completed: prepared artifacts/source, kernel, all three whole original images, private scratch, local/WSL result and serial bytes, boot guards, and the single terminal reply/token observation matched. See `baremetal-sdk-original-init-qemu-044/independent-verification.json`. The rejected request remains rejected; no readiness result was promoted.
