# Original graphics observation 072

## Verified outcome

- The isolated run and independent verifier completed once. See
  `original-graphics-boot-072-independent.json` and the preserved launch and
  verification outputs. The observation bound is not a clean service exit.
- Every render-service process discovered at samples 17, 29 and 41 was sampled,
  rather than selecting the highest PID only. Those snapshots contain PID1136,
  parent PID1. This does not assign a permanent architectural role or exclude
  other processes at other times.
- All twelve private, hash-specific field reads succeeded: backend/device guards
  were1, while backend device and composer remote fields were0. Constructed guards
  do not prove initialization completed or identify the exact failing branch.
- The main thread was in `do_epoll_wait`, syscall22, at all three snapshots.
  Therefore these observations do **not** support a claim that the main thread
  was sitting in the HDI `usleep` retry loop. Worker threads need separate evidence.
- Ninety-six task records cover at most sixteen threads per process per sample.
  Observed states were epoll, Binder read and futex waits. The cap means an
  unobserved later-created worker could still be doing discovery; no all-thread
  conclusion is justified.
- Original composer hotplug callback completion was not captured. EGL context
  creation and MakeCurrent evidence remain distinct from screen enumeration.

## Preservation and scope

The independent verifier retained original UID/domain checks, all twelve injected
ELF hashes, archive/kernel verification, full hashes of the three read-only SDK
images and all378 previous native raw logs. Readiness, desktop and physical-board
verification remain false. No target-memory writes, ptrace attach, fabricated
identity/callback, host SSH, Ubuntu changes or physical display operations occurred.

## Next boundary

Keep the working software Mesa and original service binaries unchanged. Extend
the bounded passive task coverage, including actual thread names, before blaming
the named-service lookup or changing compatibility/security behavior.
