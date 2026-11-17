# Commercial 017: explicit initramfs hardware directories

Status: one controlled attempt completed and Ubuntu was observed again on
2026-11-13 at 11:58:22 UTC. Original commercial graphics services performed real
FD690 GPU work, but the desktop did not start. Do not rerun this numbered trial.

## Change and offline verification

017 adds thirteen explicit parent directories missing from 016. The bootstrap
and all hardware-driver bytes are exactly those of the preserved 016-r2 build.
The original commercial init, service binaries, identities and authentication
checks remain unchanged. The normal GPU API parameter selects OpenGL for the
MateBook's own commercial-runtime-linked FD690 backends, not the Kirin Mali
launchers. No SDK system libraries are included.

The four initrds are loaded in this order:

1. Immutable commercial 001 Linux harness/base.
2. Small 017 archive: directories and final 017 init.
3. Immutable 016 hardware archive, now with its parent directories present.
4. The same 017 archive again, restoring the new operational run identity.

Ordered extraction was checked against every byte and mode of the full 017
archive, including directory availability before each hardware member. This
reuses existing hardware bytes rather than copying another six megabytes to
EFI. Only 348,950 bytes of new archive data were installed; its SHA256 is
`6e806d98c1ffa385a9869da996439d4d44e4601d859c0d754c95c4e57d6651c7`.
The existing 016 archive is independently hash-guarded before installation.

Installation retained all 112 existing EFI file hashes, firmware entries,
Ubuntu default and the old manual GPU entry. The custom screen-off timer stays
disabled. EFI free space is 33,251,328 bytes; the explicit reserve for this small
addition is 31 MiB rather than the previous 32 MiB. No old files were deleted.
Actual native non-PID1 execution guards rejected both harness binaries with 77.

## Runtime evidence

The retained safety limits are 8 GiB of fresh volatile guest data, measured
memory admission, a 90-second target budget, a 15-second bounded cleanup and a
210-second outer reboot deadline. These software limits cannot guarantee
recovery from a wedged kernel. Network return alone is not automatic-exit proof.

All 59 evidence files were retrieved read-only with matching remote/local hashes;
the original LAB filesystem journal was not replayed and the partition was
unmounted afterward. The target timeout and deliberate namespace termination
were recorded. Network return alone does not establish the final cleanup result.

The original composer host (PID 701, UID 3036) reported GPU scanout readiness and
four actual two-pass GPU operations (14,362, 8,901, 2,713 and 2,627 microseconds).
Original allocator and RenderService processes remained present. The previous
Mali context errors were absent. No SDK service binaries or runtimes were used.

Three genuine scanout captures at samples 3, 9 and 15 were valid 160x256 PPMs,
but all pixels were black. All three have SHA256
`33e39d41124406e5048fd667d3cd7b34e84b29874937bd5efd0d58ff2a8d6260`.
SceneBoard installation succeeded, but no SceneBoard process was observed.

The original AppSpawn launcher repeatedly exited with code 6 before running the
real AppSpawn binary. Its provided Kirin wrapper's disassembled code returns 6
when binding its volatile Mali passthrough directory fails. The exact mount errno
was not retained; no UID, capability, sandbox or authentication check was changed
to hide the failure. A separate 018 candidate removes only this hardware wrapper
while preserving the original AppSpawn executable and exact argument boundaries.

Fresh post-return checks confirmed Ubuntu default/current boot, no one-shot,
disabled/inactive custom screen-off timer, unmounted LAB, unchanged firmware and
all four commercial image hashes. Of the pre-existing EFI files, only the normal
boot-managed random seed changed. Evidence is in `commercial61-native-017/`:
`runtime-analysis.json`, `post-return-verification.json` and the three PPMs.

**A working commercial desktop and physical input remain unverified.** GPU
execution or successful package installation alone is not desktop acceptance.
