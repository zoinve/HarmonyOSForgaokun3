# Extracted composer client-buffer methods: GPU experiment003

## Verified result

The exact reference `wait_fence`, `valid`, `SetDisplayClientBuffer` and
`ClearDisplayClientBuffer` method bodies passed a real transported DMA-BUF and
native sync_file test on the MateBook under the Ubuntu kernel. Reference source
SHA-256 remains `9d2536a61c40aef948f48c482a081cdc2794d832d0775cee6bd9de87bdfa1b5a`.

Producer3818 and separately executed consumer3819 ran the OHOS probe on FD690.
The consumer passed the received buffer/fence to the extracted reference method,
verified its distinct CLOEXEC retained FD, then closed both caller-owned FDs.
It imported from the retained FD, called the actual clear method and checked
that the retained FD was closed. The imported buffer still mapped to exact
opaque red and blue pixels. Producer GPU readback, independent GBM mapping and
native-fence reimport checks also passed. Probe exit0; no new kernel log or
FD-identity warning was captured.

## Independent evidence

`baremetal-composer-probe-run-003/independent-verification.json` verifies all ten
archive and deployed ELF sizes/hashes, exact contract markers, separate PIDs,
pixels and live pre-start sandbox policies. Only renderD128 was allowed; card0
admission was denied. Ubuntu boot ID/default were unchanged, no one-shot or
consumed diagnostic entry remained, and GDM was already logically off. The
verifier refused all display setters; physical darkness was not observed.

Archive: 6,479,454 bytes; SHA-256
`8645ede484ff8cbc28ca63932c47888a84bb4a3be3314626d237f672a441dc65`.
The host C-bridge metadata/lifecycle test also passed. The older characterization
fixture now uses the actual extracted PARAM=-3 constant rather than PARAM=-2.

## Scope

This is a private reduced-state bridge around extracted methods, not the full
reference composer library or HDI ABI. Its private NDK C++ mutex ABI does not
prove the target platform's std::__h container ABI. No InitDisplay, Commit,
KMS/modeset, physical scanout, RenderService integration or identity mutation
was performed. This new method-level experiment ran on Ubuntu, not yet under
the custom native diagnostic kernel. It does not prove an initially unsignaled
fence or full HarmonyOS desktop readiness.

Failed package001 omitted a protocol-header literal; package002 stopped at an
unused reference constant under strict Clang compilation. Both outputs remain
preserved. Fresh003 restores the literal and statically checks the unused
UNSUPPORTED constant without changing reference method bodies or disabling
warning-as-error checking. Completed experiments must not be rerun.
