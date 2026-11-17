# Fixture 163: reproduce EINVAL, verify current-namespace reopening

The first attempt contains a build-only unused-function warning; no target run
started. That compile record was preserved. The compile-fix-1 attempt references
the unused key routine without calling it, preserving warnings-as-errors and
ensuring no private key is read by this fixture.

One bounded native ARM64 Ubuntu fixture opened synthetic log FDs in the parent,
then cloned new mount/PID namespaces, matching native 161's important ordering.
The unchanged bind function failed at item 1 stage 5 with EINVAL (22), reproducing
the actual native failure. This differs from fixture 160, which opened its files
after unshare and therefore did not reproduce the descriptor-origin condition.

The new helper resolves only fixed diagnostic log locations, opens them with
root-anchored openat2 and NO_SYMLINKS/NO_MAGICLINKS in the current mount namespace,
and requires the same device/inode as the inherited original descriptor. It then
binds via that newly opened descriptor. Both hilog and native synthetic log binds
succeeded; writing through the bound destination failed with EROFS and appended
source data remained visible. No raw HarmonyOS log or key was read or exported.

Result and source/header/binary hashes:
live-debug-log-fixture-163-compile-fix-1/result.json.
The fixture preserved outer mountinfo and Ubuntu boot ID and left an empty
mountpoint after private tmpfs/namespace exit. This verifies the fix in that
fixture, not yet an authenticated HarmonyOS live connection.
