# Native 164: current-namespace log reopen with original inode verification

Keep the complete original-service desktop baseline and native init 159 unchanged.
Use the existing compact loader arrangement with a distinct 538-byte overlay,
staged root-owned helper, and immutable numbered evidence. Existing native 159
opt-in and fixed read-only diagnostic commands/authentication remain unchanged.

## Evidence-driven change

Native 161 identified item 1 stage 5 EINVAL at bind mount, before key handling.
Native ARM64 fixture 163 reproduced that failure with log FDs opened before
clone(CLONE_NEWNS), then verified that reopening the same inode in the current
namespace permits the bind. Read-only destination and append visibility passed.
No original log or key was read by that fixture.

Helper 164 resolves only /mnt/lab/.../interactive-hilog030.log or the exact native
/run/diagnostic.log path. It uses current-root-anchored openat2 with NO_SYMLINKS
and NO_MAGICLINKS and requires device/inode equality with the inherited original
FD. Only the resulting current-namespace FD is passed to the unchanged read-only
bind/remount check. Both reopened FDs are closed, while original FD cleanup,
RAM-only host-key copy, isolated mount/PID namespaces and timeouts remain intact.

The helper hash is 8fa59cdd2cf8beb7efb9271d39e7bee5ffb5bf2a0efea73df8e35d097f231918.
The log-header hash must match the verified 163 fixture. Helper regeneration and
byte-identical static recompilation are admission requirements. The complete
29-archive chain changes only /live-debug159 into the hash-checked loader.
No prior EFI payload is modified or removed and the 32 MiB reserve is retained.

## Verification scope

The first admission attempt failed because a unit-test wrapper discovered zero
tests; no deployment followed. Its outputs remain unchanged. The corrected wrapper
runs in its real main-module globals, and the explicit loader-test-fix-1 admission
records new test outputs separately. All 17 focused/baseline scripts passed.
Two additional analyzer regression tests require current-namespace/inode success
for both logs as well as inherited namespace matching, authenticated current-IP
connection, log growth, completed follow, shell refusal and clean reaping.

One new bounded operational boot is planned after installation/retention checks.
Transport success, if obtained, does not prove full process-debugger attachment,
Settings repair, physical touch or native USB-service acceptance. The full driver
objective remains active; USB public service identity 4201 is independently
confirmed read-only in usb-dump-contract-162, not a runtime device-list result.
