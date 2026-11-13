# Native presentation 043 — build and independent audit, not a new device run

## Outcome

Added real KMS completion telemetry beside the existing native 041 pipeline. The new AArch64 composer builds, and an independent read-only audit passed. **It has not been installed or executed on the MateBook. Stable 120FPS is not verified.**

This continues the existing native FD690/original-service work; it does not replace that history with the earlier QEMU software-rendering timeline. Historical 041's 32 GPU operations averaging 4.148 ms are composition-stage samples, not desktop FPS. Physical touchpad click/drag, status-bar completeness and sustained 2560×1600 presentation acceptance remain open.

## Instrumentation scope

- Records the actual `page_flip_handler` sequence, seconds and microseconds, local monotonic submit/callback times, framebuffer and submission ID. The real `DRM_CAP_TIMESTAMP_MONOTONIC` query labels the timestamp clock; an unknown/realtime clock is not silently accepted as monotonic.
- Separates normal **client** submissions from the existing idle **cursor** worker. Initial modesets, failed submissions, ambiguous overlaps and orphan completions do not become accepted client presentations.
- Rendering, real fences, KMS operations, actual callback state updates, cursor ownership, input and the existing software vblank ticker are not replaced. The source transformation reverses exactly, apart from the independently checked build-local cursor-header filename.
- Submission IDs identify submissions, **not distinct visual content**. The analyzer never certifies 120FPS, steady workload, thermal behavior or physical presentation from these records alone.
- Uses the existing precreated diagnostic file under the original composer UID 3036. No permissions, original service identities, authentication or policy checks were changed. That existing writable diagnostic file is not cryptographic identity attestation.
- Sampling is bounded to 4096 records, with 16-completion flush batches. Abrupt process termination can lose an unflushed tail; explicit caps, logging errors and missing records are not full-workload evidence.

## Build and independent evidence

New artifact: `native-presentation-043/libdisplay_composer_vdi_impl.z.so`, 87,360 bytes, SHA-256:

`62a41ba00c97ffac4bd23e6805589c2dc2896c507718025783ac3a5bb25692ef`

Independent report: `native-presentation-043-independent/result.json`:

- Four generated artifacts match their WSL and local copies; the ELF is AArch64 ET_DYN with the expected SONAME and no foreign glibc/libstdc++ dependencies.
- All **72** required existing C exports remain.
- **22** guarded inputs and **8** frozen header copies match; source reversal matches the original 041 composer and cursor source.
- All **71** existing native 041 raw evidence files still match their retrieval manifest. This is a fresh local preservation check, **not another native 041 boot**.
- Existing 041 raw evidence contains **zero** `NATIVE_PRESENT043` records. Running the new analyzer on its final `phase-069.log` therefore yields no completion window; it cannot retroactively establish its FPS.

Historical 041 did not record every transitive header hash. The new audit does not claim byte-equivalence between the new build inputs and the historical 041 ELF. Runtime dependency closure and actual hardware callback collection remain unverified for this new artifact.

## Tests and preservation

Explicit offline checks: telemetry/source/build gates **3 passed**, analyzer **3 passed**, independent-audit gates **1 passed**. Missing implementations and the flush requirement were observed failing before implementation. Synthetic host state-machine/trace fixtures are not GPU tests. The analyzer rejects failed/unmatched/wrong-UID/unknown-clock/conflicting records, deduplicates cumulative snapshots and does not let cursor updates inflate client rate.

Completed build and audit were each run once, with new exclusive outputs. No old build, boot, runtime or operational verifier was replayed. No SSH/device access, installation, reboot, synthetic input, original-image write, Ubuntu configuration change, push or commit was performed in this work.

## Remaining evidence needed

A fresh, separately numbered native runtime would need verified deployment and return safeguards, actual callback records, real changing-content/interactive workload, sustained intervals and refresh sequence coverage, latency, misses, thermal/clocks and physical input observations. Instrumentation overhead and sampling bounds must be included. Neither panel refresh rate nor a short GPU operation is acceptance for stable 120FPS.
