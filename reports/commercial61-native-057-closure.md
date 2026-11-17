# Commercial native 057 closure

## Result

One bounded boot ran 2026-11-14T16:37:08.816932Z to 16:40:50.991920Z,
returning to Ubuntu boot 20e7be42-04c5-4696-84b1-566279213f27. All 64 files
matched remote retrieval hashes, using read-only/no-replay access. The target
timed out as configured (exit 9); the observer stopped. All seven sparse
scanout captures remain black. No authentic desktop or interaction is proven.

## Actual Branch Observation

The observer now samples x0-x6 plus x9 with ARM64 mask 0x27f and exact 104-byte
perf records. Kernel UAPI register ordering and the synthetic wrapped-ring
test were checked, including explicit x9=0x12 extraction. Entire executable
mapping comparison remains read-only; original instructions and private
objects are not modified or dereferenced.

184 successful attachments; zero failures, lost samples, malformed records,
suppressed log records, or instruction mismatches. There were 290 samples at
the original OnDraw return from CheckRenderSkipIfScreenOff, VA 0x41f504;
all x0 values were zero. Of those, 66 were after SceneBoard's first ArkUI
flush at 82.586 guest seconds, also all zero.

The initial zero-field gate at VA 0x41f240, missing-parameter branch at
0x41f250, and common reason store at 0x41f3b4 had zero samples/counter hits.
That common store covers the audited screen-state-invalid and screen-power
skip paths, not every OnDraw exit. Other return paths store reasons at their
own instructions. Do not infer absence of all skip paths from these zeros.
Periodic attachment still limits complete thread-lifetime coverage.

The last Composer frame was 78.247586 seconds, before the first flush;
no post-flush frames were recorded. Thus 057 does not support missing
parameters, an empty child-display gate, or observed screen-power skipping as
the cause. Continue into intermediate frame/dirty-region checks, preserving
the genuine desktop objective and original security checks.

## Supporting Source

OpenHarmony graphic_graphic_2d branch OpenHarmony-6.0-Release was resolved by
git ls-remote to commit 0fa4396a14a9717472a45ca45f184338760f720a. Its OnDraw
initial child-display-count condition corresponds structurally to the initial
commercial branch investigated, but this is not a binary identity claim.
The direct original-binary observation did not hit that branch, rejecting it
as the current supported explanation. See commercial-screen-source-audit-057
for pinned external source files/hashes when its fetch completes. No source
from the internet was deployed onto the device.

## Preservation

Ring/memory/specification, workflow and ordered-overlay tests passed. Compared
to 045, only init changed; bootstrap, original userland and modules retained
their bytes. Ubuntu current/default, screen-off timer enabled/active, original
manual entry, firmware and four original image hashes passed return checks.
119 prior EFI files matched, accounting for the boot-managed random seed and
authorized archived removal of entry 055. Shared payloads remain. Entries
056/057 are retained; retention stamp 20261114T163658988048Z.

Next low-frequency candidates are the original SkipFrame result at VA
0x41f8e8, CheckScreenNodeSkip result at 0x4209dc, and intermediate return
reasons at 0x41fd08 and 0x4205e0. Audit each surrounding branch before using
it. Do not repeat known-denied HiDumper requests or alter completion/security
state to obtain a drawing result.

Sources: commercial61-native-057/{boot-observation.json,hwbreak-analysis.json,
render-analysis.json,runtime-analysis.json,hwbreak-test.json}, retrieval
manifest, commercial-render-audit-057/result.json, and
commercial-return-audit-057/result.json.
