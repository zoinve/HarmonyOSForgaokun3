# Original samgr: bounded live tracing, trial 033

## Outcome

The real context-manager ping still returns `BR_DEAD_REPLY` (`0x7205`). Trial 033 remains a failed readiness test. Original samgr executing in `u:r:samgr:s0` with UID/GID 5555 is not evidence that the service registered or became ready.

Four policy-authorized, direct-child ptrace samples obtained real ARM64 register sets (272 bytes); all four detach operations succeeded. The probe only reads registers, maps and bounded frame-pointer chains. It does not change child memory, registers, tokens, production policy or enforcement.

## Observations

- Two sampled PCs map into original SDK libc; two others map into libc socket-related code, with a caller in the original fwmark client.
- Recorded frames repeatedly include original libc, `libsystemparam.z.so` and `libhilog_inner.so`. No sampled PC was in the samgr executable itself.
- Original parameter-client code opens/connects a UNIX socket and logs errors on the failure path. The original init binary references `/dev/__parameters__/` and `/dev/unix/socket/paramservice`.
- A subsequent symbol audit locates `InitParamWorkSpace`, `GetParamWorkSpace`, and `InitParamSelinux` in the **original SDK libc**, not in libsystemparam or libbegetutil (which import the workspace functions).

These observations support investigating missing original parameter/logging bootstrap before manually launched samgr. They do **not** establish a sole root cause, complete stack unwind, or faithful original init execution. Dynamic-symbol proximity is not a reliable name for hidden functions. Mapping reconciliation uses ELF load segments; pointer-authentication bits are masked only in offline address analysis, never disabled in the guest.

## Preservation and limits

The runner verified unchanged native configuration, critical source files, test kernel/configuration and the whole original read-only system image. The unchanged production policy remains enforcing. Binder debugfs reads denied by that policy were not bypassed. No MateBook reboot, host installation, SDK image write, network attachment or GPU test occurred.

Evidence: `baremetal-selinux-qemu-033/{result.json,serial.log}`, `baremetal-sdk-samgr-trace033-{mapping,source}.json`, and `baremetal-sdk-param-libc-audit005.json`.

Independent verification subsequently checked both prepared files' sizes/hashes, the actual test kernel, the whole original system image, byte-identical local/WSL result and serial copies, and four successful ARM64 register samples/detaches. It also explicitly preserved the failed readiness result. See `baremetal-selinux-qemu-033/independent-verification.json`; serial SHA-256: `d5aa08ecfd18ba6a6f02be903d1de56c79a4ddcd9784fcccaa516e79756f2e14`.

## Next controlled investigation

Determine the original init/server initialization sequence and required filesystem layout before another readiness trial. Prefer original init and genuine parameter initialization over guessed workspace formats, invented parameter values, logging/security bypasses or replacement service managers. Keep existing failed trials immutable and use fresh output numbers.
