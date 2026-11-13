# Original SDK Binder transaction regression 011

The original SDK C Parcel API and `BinderInvoker::SendRequest` completed a real synchronous request/reply in diskless QEMU against the identity-patched kernel. The original shared libraries were extracted read-only; none were patched or replaced by success stubs.

- Original Parcel request: code `0x510`, eight-byte payload `0xabc010`.
- The raw test service checked UID 0, actual client PID, self token `0x5000000000000500` and first-caller token `0x6000000000000600` through both kernel identity interfaces.
- Original `SendRequest` returned 0; the original Parcel API decoded response `0xdef010` and the client's own task tokens remained unchanged.
- The earlier raw synchronous, one-way and nested callback tests, original token APIs, connector negotiation and nonmutating diagnostic helper also passed in this run.

Independent verification checked all 28 RAM files' sizes/hashes, local/WSL result and serial equality, failure/panic absence, and the unchanged test kernel hash `130f30abc9c9fc8faf1fb84bec268a1cde10fabdc3c93839250f347924f27bad`. Serial SHA-256: `8c11f50a73035dbccf0ba24d7463af9f2492be7d2531c461006e720489f87c59`.

The adapter uses original C API allocations and exported original nonvirtual C++ methods. Its extraction of the C wrapper's MessageParcel pointer and construction of the eight-byte MessageOption are limited to this exact disassembled SDK build, not a portable public ABI. The initial 010 harness failed strict compilation because retaining its Binder mapping left a parameter unused; 011 marks that parameter used without changing kernel code. Failed 010 outputs remain preserved.

This tests an original SDK client against a raw test service, **not yet an original SDK receiving callback**, full token services, concurrency/death recovery, all SPM callers, physical-board IPC, or a HarmonyOS desktop. No physical reboot, disk/network/GPU attachment or Ubuntu configuration change occurred.
