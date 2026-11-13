# Genuine SA query 045

## Scope

Continue after completed 044, without rerunning or replacing its evidence. The pre-boot observer's own token zero legitimately fails the original List native-token gate. No token, SID, permission, or policy workaround is introduced.

The unchanged original CheckSystemAbility proxy uses code 2, the same `ohos.samgr.accessToken` descriptor, an int32 SA ID, and flags `0x200000`. The request reuses the original SDK-encoded prefix verified in 042 and encodes SA 1912. Its SHA-256 is `349e6ff8c1f2b9930e29ac73c93c149e2917774f9e61b692cbd51bcc8c417a7b`. Read-only server analysis is recorded in `baremetal-sdk-samgr-check045-audit.json`: the Check handler reads the ID, performs its own service-policy check, and writes a remote object only when found. The List authorization result is not reinterpreted as Check authorization.

## Validation and preparation

The actual C decoder was tested against a valid remote handle and malformed status, offsets, mapping bounds, FD object type, and zero-handle responses. The generated init passed strict host compilation and actual non-PID1 refusal before preparation.

Prepared ARM64 init: 784,888 bytes, SHA-256 `8c9e08d6bdd948fb5ef50c13e55f8355ca73d756a2832c1c31d6224963658ae8`; source SHA-256 `3e0ab27a5c62ef4eb5104ee1d36e1d147d349f2589c5ffc60840a5b0b181d88d`.

The bounded original-init observation uses the unchanged kernel, original SDK images attached read-only, original hardware/fstab contract, enforcing SELinux, and only a fresh private scratch filesystem writable. The SDK chooses its own policy; the separately extracted production-policy reference is not injected. Authorization errors terminate; original Check status 7 (object unavailable/read failure) is condition-retried only for this already validated request. A successful transport must also contain exactly one bounded nonzero remote Binder handle from UID 5555. Merely receiving bytes does not constitute success.

## Runtime status

045 completed its 60-second bounded observation. It received exactly one genuine UID-5555 status-code reply: transport status 1, payload `01000000`, no Binder object. The observer read its own actual token as zero (original SDK type -1), then stopped the rejected query with SELinux still enforcing. This is not an empty result or successful SA lookup. There were 40 registration log records, not proof of full service readiness.

Independent verification confirmed prepared files and source, kernel, all three whole original images, private scratch image, and byte-identical local/WSL result and serial evidence. Original images, kernel/configuration, and guarded source files remained unchanged. See `baremetal-sdk-original-init-qemu-045/independent-verification.json`. No physical reboot or Ubuntu modification occurred.
