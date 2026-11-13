# Original graphics graph 073: worker sampling and missing ashmem integration

## Verified observation

- `reports/original-graphics-boot-073-independent.json` independently verified the
  original graph, 12 injected provider files, archive/kernel, three full SDK
  images and all 378 earlier native raw files. No host boot changes were made.
- Three bounded task snapshots produced 159 records (53 task observations,
  three files each), covering 19 distinct TIDs. The original main thread waited
  in epoll; observed workers waited in Binder, futex or epoll paths. No sampled
  thread was in nanosleep. These are snapshots, not a continuous execution trace.
- Twelve successful, hash-specific state reads still showed constructed backend
  and device guards, but null backend device and composer remote fields.
  There was no captured completed composer hotplug callback. Neither desktop nor
  physical scanout is verified.

## Corrected interpretation and integration omission

The original client can return null **after obtaining the remote composer** if
its genuine SMQ requester initialization fails. Consequently, a null stored
composer pointer does not establish a service-discovery failure.

Reviewing HarmonyMac's `ports/tools/prepare-render-service-test.sh` revealed an
omitted prerequisite in the full original-init fixture: loading a matching real
ashmem module before starting original services. The current virtual kernel has
no built-in ashmem, and fixtures through 073 did not load the reference module.
This is an integration omission, not proof yet that it caused the observed null
client. No callback, queue, identity, token or successful return is fabricated.

## Matching module build and retained failures

- Builds 001/002 refused or failed because the Image-only kernel output lacked
  `Module.symvers` / `scripts/module.lds`. Failure evidence remains numbered.
- Build 003's copied Kbuild Makefile redirected `modules_prepare` to the original
  virtual kernel output, generating build-support files there. This unintended
  side effect is recorded; those files were not deleted or silently reverted.
  Image, config, symbol inputs and reference source hashes remained unchanged.
- Build 004 explicitly used the source tree with `O=` pointing to its own copy.
  It built the real reference module without unresolved-symbol waivers.
  `reports/original-graphics-ashmem-004/result.json` records the 13,400-byte module,
  SHA-256 `951e58dceffa3bc00abeab793b4dcbd8d846644d08524e5128aaff7f2c6c493d`.
  Its sole source adaptation is fixed-4-KiB `PAGE_SIZE`; reference operations,
  including capability checks, are retained. A matching release string alone is
  not authorization to load this virtual-kernel module on Ubuntu or native hardware.

## Next experiment

074 adds exactly this hash-pinned module to the isolated guest. Loading is behind
PID1/root, explicit diagnostic command-line and virtual-machine model guards.
The fixture checks that `/dev/ashmem` is a real registered kernel character
device before snapshotting genuine device nodes and handing off to original init.
Providers, original services/credentials, policy and permissive mode are unchanged.
The bounded virtual run is pending; module load, SMQ recovery, hotplug and screen
enumeration must be evaluated from its actual evidence, not presumed successful.
