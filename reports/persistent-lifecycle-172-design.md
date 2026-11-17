# Explicit persistent-data mount teardown 172

This is a tested source transformation, not an installed or booted candidate.
No remote target access, data-image writes or original evidence changes occurred
during the recorded tests. Repaired source state from operation 171 is untouched.

## Observed Gap

Boot 168 mountinfo includes the writable loop3 filesystem at both `/data` and
`/mnt/hmdfs/100/account/device_view/local`. Its old finalizer remounted loop3 in
another namespace, synced it and unmounted that new path. Those successful calls
did not directly demonstrate cleanup of the original mounts. Offline fsck then
found 110 orphan-list inconsistencies. This association is not proof that mount
lifetime is the sole cause of the inconsistency.

## Change

`persistent-lifecycle-172.py` changes only the outer lifecycle inherited from
168. Original bootstrap/runtime, service configuration, authentication and desktop
logic remain unchanged. It pins the actual target mount namespace and root after
stopping the diagnostic sidecar but before terminating the target. Cleanup requires
successful waitpid reaping of that same target; it cannot infer exit from a timeout.

The bounded cleanup worker enters the retained namespace/root, verifies `/data`
is loop3, and syncs it. It reads its own updated mountinfo through an outer proc
directory descriptor that survives the root change. It selects every loop3 alias,
all mounts below `/data`, and descendants of the aliases even outside `/data`.
It unmounts leaf-first without lazy/forced unmount, then rereads mountinfo and
requires zero remaining selected mounts before syncing the backing file and LAB.

Malformed/oversized tables, duplicate IDs, ambiguous overmounted paths, selected
root mounts, cycles, busy mounts, identity mismatch or unreaped target cause refusal,
not fallback to the legacy remount-only finalizer. Legacy finalizer code remains
compiled through the unchanged 166 header but is never called by this path.
The log explicitly does not claim graceful original-service shutdown: the existing
bounded diagnostic still kills target PID 1 when its observation budget expires.

## Recorded Verification

`persistent-lifecycle-172/result.json`, `tests.stdout` and `tests.stderr` record
three test methods with unchanged source hashes and successful completion:

- Planner cases include aliases, nested mounts, escaped spaces, malformed input,
  duplicate IDs/paths, selected root rejection and cycle refusal.
- Host object compilation and actual ARM64 static linking with warnings as errors.
- Repeated ARM64 build bytes match; QEMU execution outside PID 1 returns 77 before
  mount or block-device work, preserving the existing guard.
- Real temporary tmpfs bind aliases and a nested mount are removed in an isolated
  WSL mount namespace; an unrelated mount is preserved.
- A separate real child namespace is pinned, its child is killed and reaped, then
  entered after exit. Root change, proc descriptor access, mount-table reread and
  alias cleanup succeed without exposing the target or original images.

These real-mount tests validate the planner and namespace approach using tmpfs,
not the actual HarmonyOS ext4 image or custom native kernel. They are not physical
driver, desktop, original-service graceful shutdown or recurrence-prevention
acceptance. Native admission, a new immutable boot, evidence retrieval, and an
offline fsck gate remain necessary. Warm-start SceneBoard readiness is still
unresolved and must not be presented as fixed by this lifecycle change.
