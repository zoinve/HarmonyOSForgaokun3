# Native original-service trial 002: root-directory failure isolated

## Actual result

One physical boot completed and automatically returned to Ubuntu. The trial's
49 raw snapshots are preserved under `native-original-graphics-boot-002/native-logs`.
Ubuntu boot ID after return: `754ad049-ece2-4548-9fee-17823b353a20`.
Three original images and 79 static EFI files matched their recorded hashes;
the expected boot random-seed rotation is recorded separately. Ubuntu remains
the persistent default, the screen-off timer is active, and Ubuntu's active
LSM list remains `capability,landlock`. LAB was restored read-only, noload.

## Failure evidence

In `phase-049.log`, sample 0 can stat `/proc/1/root/data`. Samples 1–11 cannot:
`rc=-1 errno=2`. The observer's own `/data` remains present on loop3, with
its original mount and populated directories. PID 1's later mountinfo instead
contains `/native-target/data`, `/mnt/lab`, and `/mnt/ubuntu`, proving that its
root view has changed back to the outer diagnostic root. Original init logs
real failures to find `/system/bin/sa_main`, create data directories, and start
RenderService, Foundation, allocator and composer. None of those monitored
services was observed alive; this is not EGL or desktop success.

SELinux enforcement samples are all 0 and labelled AVCs have `permissive=1`.
The verbose kernel ring no longer retains the initial policy-load audit.
The first independent verification correctly failed that overly specific
retention assertion; the verifier now separately reports active labelled
policy evidence and `early_policy_load_audit_retained=false`. No raw log was
changed or regenerated to satisfy verification.

## Independent reproduction and scoped correction

`next-experiment/native-root-namespace-regression-003.c` uses only a disposable
private mount namespace and a 1 MiB tmpfs. On the real MateBook, entering a mount
namespace after chroot resets `/` to the namespace root: the original form
returns 1 with `stable=0`. Creating a genuinely rooted namespace using Linux
`open_tree(OPEN_TREE_NAMESPACE)` and entering it returns 0 with `stable=1`.
Results and binary hash are in `native-original-graphics-boot-002/root-namespace-regression.json`.
No target service, GPU operation, policy load or boot occurs in this regression.

This explains how original init's namespace management defeats chroot-only
setup. Candidate 003 changes only outer root-namespace creation, retains the
002 bootstrap byte-for-byte, and refuses to fall back to chroot. Its real
original-init outcome must still be checked after the separate physical boot.
