# Commercial 018: original AppSpawn without the Kirin passthrough launcher

Status: one controlled attempt completed, with original AppSpawn recovery
verified. **The commercial desktop is still not running.**

017 proved real FD690 operation through the original commercial graphics
services, but captured black frames. Its original Kirin AppSpawn wrapper exited
with code 6, the wrapper's bind-mount failure return, before the actual AppSpawn
executable. The volatile Mali passthrough source directory is not part of the
fresh guest data. The precise failing mount errno was not captured.

018 changes only the RAM-overlay board launcher at the existing script path.
It directly executes the original `/system/bin/appspawn`, preserving every
argument, including the provided quoted multiword arguments and application
sandbox-on option. Original init service definitions, UIDs, groups, permissions,
capabilities, security labels and commercial binaries remain unchanged. No
identity or authentication compatibility shim is introduced.

The original script is saved beside the transformed script in the numbered
report directory. Unit tests and a comparison against the actual ISO-provided
script verified exact argument preservation. Both native harness guards refused
execution outside isolated PID 1. All 114 pre-existing EFI file hashes remained
unchanged during installation; Ubuntu default, firmware, old manual GPU entry
and disabled screen-off timer were preserved. No original images were written.

The archive chain is commercial 001 base, 017 directory archive, immutable 016
hardware archive, then the new 018 overlay. Ordered extraction, all final bytes
and modes, and parent-directory availability were checked against the full 018
archive. Only init, bootstrap and the new hardware launcher differ in the final
overlay. Its 699,165 bytes have SHA256
`b259b4814154d13285fe7b33c5bf4497035aa0d003cefa43e3f250bd3287013e`.
EFI free space after installation was 32,542,720 bytes, above the explicit
31 MiB reserve. No old archive was deleted or overwritten.

Safety limits remain 8 GiB fresh volatile guest data with measured memory
admission, a 90-second target budget, bounded 15-second cleanup and independent
210-second outer reboot deadline. These software limits cannot guarantee
recovery from a wedged kernel. Runtime acceptance requires the original
AppSpawn to stay alive, original SceneBoard to launch, and actual visible
desktop/scanout evidence—not merely a process, installation result or GPU call.

## Actual result

The attempt ran on 2026-11-13 from 12:11:38 to Ubuntu reachability at 12:14:04
UTC. The configured target timeout and termination are in the guest logs.
Ubuntu boot ID is `c60cff7b-58f3-49ee-9664-c4d51199b1f0`. Retrieval preserved
59 files with matching remote/local hashes; the original evidence partition
was mounted read-only with `noload` and then unmounted.

The original AppSpawn now finishes ArkVM preload, loads its original sandbox
configuration, reports its startup event, and creates application children.
Its old immediate exit code 6 is gone. However, those children fail the
original seccomp setup: `seccomp_policy.c:237 get filter name failed`, then
the original AppSpawn hook returns `-22`. SceneBoard installation succeeds,
but its process was not observed. All three actual scanout captures remain
black. GPU operation alone is not desktop acceptance.

Read-only inspection of the original security library places this failure in
`GetCfgFiles` lookup before filter loading or the kernel seccomp call. Original
filters exist under `/system/lib64/seccomp`; the application sandbox exposes
that library tree but lacks the configuration layer's `/usr/system/lib64`
pathname. A narrow alias is being tested separately; no filter, sandbox switch,
identity, permission, or security failure check has been disabled.

Post-return verification rehashed all four commercial images against the ISO
originals. Ubuntu default, firmware, manual GPU entry, disabled/inactive screen
timer and unmounted evidence partition were preserved. Of 114 pre-existing EFI
files, only boot-managed `loader/random-seed` changed; it was not restored.
See `commercial61-native-018/runtime-analysis.json` and
`commercial61-native-018/post-return-verification.json` for numbered evidence.
