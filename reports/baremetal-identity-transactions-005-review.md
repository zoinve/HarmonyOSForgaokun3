# Binder identity transactions: real-kernel regression

## Verified results

The diskless QEMU guest uses the separately console-enabled identity test kernel, SHA-256 `130f30abc9c9fc8faf1fb84bec268a1cde10fabdc3c93839250f347924f27bad`. No physical-board boot, disk, network or GPU was involved.

- Run 003 passed 132 checks, including two synchronous caller/reply exchanges and one-way delivery after the caller exited. The receiver saw the actual originating token pair and PID. Its own task token was not overwritten.
- Run 005 passed 180 checks, retaining the previous cases and adding an actual nested caller → manager → caller callback using a kernel-translated Binder object handle. Both sides verified the peer identity and reply payload. The callback caller changed its first-caller token through its authorized supplementary group; the nested reply carried that new value without changing the manager's own task token or first-caller token.
- `baremetal-identity-qemu-005/independent-verification.json` independently checks both runs' local/WSL serial-log byte equality and the unchanged test-kernel hash.

The nested test verifies the kernel's last-delivered caller cache and task-identity separation. It does not claim automatic restoration of the kernel cache to an outer caller. The original SDK IPC implementation's own invoker identity save/restore remains a distinct userspace behavior.

## Preserved failed experiment

Run 004 stopped at `nested manager Binder mapping errno=16`: the test attempted a second mmap on the same Binder open after unmapping its first mapping. No kernel identity assertion failed. The fresh 005 harness keeps one continuous manager mapping across both regressions; the kernel was not patched or rebuilt to make that test pass. The failed 004 log and init remain unchanged.

The serial logs also contain an undelivered `TRANSACTION_COMPLETE` notification when the deliberately exiting one-way caller closes. This is retained evidence, not silently suppressed.

## Limits

These are static ARM64 raw-Binder test clients. They do not establish full original SDK IPC-library compatibility, concurrent stress coverage, complete Binder death-recipient behavior, physical-board operation or HarmonyOS desktop readiness. Test token values and the permissive private Binder device exist only in the explicitly opted-in, diskless QEMU test.

An additional 006 experiment packages the unmodified SDK token library and original OHOS loader for direct API-level checks. Its preparation is separate from these verified transaction results.
