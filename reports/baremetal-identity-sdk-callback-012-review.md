# Original SDK nested callback: isolated kernel test 012

## Verified result

The unchanged SDK IPC libraries completed an actual nested Binder callback in
the diskless ARM64 test kernel. The SDK client exported a genuine C-API-created
remote stub in its outgoing parcel. The raw context manager invoked the
kernel-translated handle while the original `BinderInvoker::SendRequest` waited.
The original SDK dispatched that incoming call to the registered C callback.

Inside that callback, the original public SDK functions verified:

- An active incoming transaction, the actual code and request parcel value.
- Full calling token `1122334455667788` and first token `8877665544332211`.
- Actual caller PID 1 and UID 0, separately from its own unchanged task token.
- A real reply parcel, subsequently read and checked by the manager.

After the outer synchronous request returned, the SDK reported no incoming
transaction and restored its own full tokens, PID and UID. Its original
token, connector and parcel tests also passed. The raw synchronous, one-way,
nested and non-mutating diagnostic tests from previous iterations remained.

`baremetal-identity-qemu-012/result.json` records the actual run; an independent
follow-up checked all 28 RAM files and init against sizes and SHA-256, the exact
test kernel, and equality of local and WSL result/serial records. Serial SHA-256:
`7ec4e71966ceddb085e86cfbbfc0e296ed43ccf54e43f8c060761822923b4485`.

## Scope and limits

No production kernel change was needed for this iteration. It reused the exact
002 test kernel; native candidate configuration and critical source hashes
remained unchanged. There were no storage, network or GPU devices attached,
no physical-board reboot and no installed system-library replacement.

The callback uses the public original C API. The outgoing request still uses
the exact-build test adapter documented in test 011, not a portable C++ ABI.
This verifies one genuine SDK receiver path and restoration after one nested
callback, not arbitrary concurrency, all IPC services, death notifications,
complete access-token services or a HarmonyOS desktop. Missing HiLog server
messages in this deliberately minimal environment are preserved in the log.
Unsupported SPM calls continue to fail honestly; no token or permission success
was fabricated.
