# Original SharedMemQueue characterization 001

## Runtime evidence

The original service's private `SharedMemQueue<int>` constructor, destructor,
`ReadNonBlocking` and `WriteNonBlocking` executed in the isolated ARM64 TCG guest.
All eight cases passed: real backing FD creation, unchanged output on empty read,
zero-size read rejection, FIFO, full-queue rejection without corruption, ring
wrap, a forked child writing into the inherited shared queue, and destructor
closure of the backing FD. No shared-memory implementation was substituted.

The original responder's `InitReply` disassembly establishes the 64-byte opaque
object allocation (88-byte shared allocation, object at +24) and SmqType=1.
Private function VAs and instruction heads were checked against the unchanged
original service. These witnesses are not a stable public ABI.

## Launcher mismatch, not erased

The archived trial returned QEMU rc0, normal child status0 and all eight case
lines, but its launcher exited with an assertion: the inherited pass detector
still expected `smq_not_tested=1`, while this probe correctly emits
`composer_request_not_tested=1`. Therefore the original `result.json` retains
`probe_pass=false`. The experiment was **not rerun** and its result was not
rewritten. Independent verification explicitly records
`launcher_marker_mismatch=true`, checks the exact new marker and normal guest
exit, and verifies all raw artifact hashes. The verifier correction had an
observed RED→GREEN offline test; three safety tests pass.

## Preservation

- Package: `reports/composer-queue-package-001/manifest.json`.
- Trial: `reports/composer-queue-run-001/`, runtime 18.71 seconds.
- Independent check: `reports/composer-queue-001-independent-verification.json`.
- Initrd SHA-256: `9d1c44dce38af5d0e2d6737f54d232009eb47f12fb26e9d9ae6b73d89798e419`.
- Serial SHA-256: `6c87e1595ff24e2b3ecd0a2cb95f2fac13a7438d4d9a8449a99398eba4521ec6`.
- All 295 other parent archive records and all 378 prior native raw files verified.
- Four local/remote trial artifacts match. Same Ubuntu boot ID/kernel and 13 EFI
  loader configs; default Ubuntu, absent one-shot, screen timer enabled/active,
  logical screen off without setters. Physical screen not observed.

## Limits / next

Fork inherited mappings only: not independent-exec queue metadata transfer,
Binder/HDI marshalling or the complete composer SMQ request/reply handler.
Nonblocking calls do not verify futex wake/wait. No service factory, DRM/GPU,
display initialization, commit, RenderService or desktop was tested. Continue
with original responder request/reply prerequisites under the same isolation.
