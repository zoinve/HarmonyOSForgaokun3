# Native original-service trial 001 — actual result

## Outcome

One **physical MateBook E Go boot** executed the original SDK init, loaded its SELinux policy and returned automatically to Ubuntu. This is not QEMU evidence. Original graphics services, Mesa use by RenderService, scanout and desktop operation were **not established**.

Evidence: `native-original-graphics-boot-001/runtime-result.json`, `independent-verification.json`, and 49 unmodified, SHA-256-verified snapshots under `native-logs/`. The last snapshot is `phase-049.log` (binary-safe inspection required: the device-tree model contains NUL).

Boot IDs:

- Ubuntu before: `6b46894a-8b4b-49a4-bf71-5a903d6b3d95`.
- Experimental native boot: `6c368db2-894b-45d3-bd17-2129eed0931d`.
- Ubuntu after: `e75dfc68-75d3-4087-8d73-ff630fa6f919`.

## What was actually observed

- Original system, vendor and sys_prod loop devices reported read-only with exact expected sizes. Fresh 512 MiB writable RAM-backed data was attached; original userdata was not attached (final snapshot lines 314–324).
- Original init ran as namespace PID 1 / physical PID 305. Kernel audit records show the genuine init process in `u:r:init:s0` and successful SELinux policy load (`lsm=selinux res=1`, lines 908–910).
- All 12 passive SELinux samples read enforce `0`; audit denials explicitly report `permissive=1`. SELinux was not disabled.
- Genuine physical DRM nodes were supplied: card0 `226:0`, renderD128 `226:128` (lines 327–328). Presence is not proof that a service opened them or that the display scanned out.
- RAM graphics/provider overlays and original HDF configuration import completed before executing original init. This does not prove that the providers were subsequently loaded by services.
- No monitored RenderService, composer, allocator, Foundation, samgr, hilogd or devmgr process/map record appeared in the observation window. Original hilog client reported connection refused, despite exiting zero; this is explicitly **not** a successful hilog-service check.
- The namespace was stopped after its bounded observation; the outer native init reached its final snapshot and returned to the persistent Ubuntu default.

## Current failure boundary, not a claimed root cause

Original init progressed through configuration/policy work but the expected original-service runtime was not observed. Final kernel logs include:

- `cgroup: Unknown subsys name 'cpuset'` and `'memory'` (1541, 1547).
- Missing secure-storage device and TEE identities/device (1556–1565).
- `Create file /data/.ro_test in /data failed![No such file or directory]` after startup mount/configuration activity (1568), even though the bootstrap successfully mounted fresh RAM data earlier.
- Numerous original-init printk lines suppressed by rate limiting, and unsupported access-token ioctl command 16 reports.

These identify unresolved early userspace/storage/kernel-interface issues, **not** evidence of an EGL/Freedreno failure. Do not change EGL libraries or service identities based on this trial. The empty native board-specific job list was compared with the real emulator configuration: common original init.cfg retains the actual pre-init, post-init and service-trigger sequence; importing the emulator's fake boot-animation parameters is not a valid remedy.

The next distinct candidate should collect unfiltered process state, original-init mountinfo/root/data state and early original-init diagnostics across this boundary. Determine whether mounts or original service startup fail before attempting a targeted fix. Do not repeat this completed numbered operational experiment.

## Host preservation and collection corrections

- All three original image SHA-256 values matched after the boot.
- 79 static prior EFI files matched their baseline. `loader/random-seed` changed normally when systemd-boot rotated it; before/after hashes are recorded, not concealed or counted as unchanged.
- Persistent Ubuntu default and loader configuration remained unchanged; no one-shot entry remained. The automatic screen-off timer is active. Ubuntu's active LSM remains `capability,landlock`, not target SELinux permissive.
- LAB was unmounted after Ubuntu returned. Evidence collection first refused the root-filesystem fallback rather than reading an incorrect path. After exact UUID/PARTUUID checks, LAB was mounted read-only with noload/nosuid/nodev/noexec, restoring its pretrial read-only state.
- The first attempted mount precondition incorrectly assumed `mountpoint -q` returns 1 for a non-mount; this system returns 32. No mount occurred on that rejection. The corrected precondition used `os.path.ismount`, then mounted only the identified LAB partition.
- The next collection correctly noticed the rotated EFI random seed. The verifier now records this expected boot-generated change separately while checking every static file.
- All failed preparation/collection outputs remain preserved. These were collection/control-script corrections; the physical boot was performed exactly once.

Fresh read-only verification passed for the 49 raw snapshots. A disposable altered-snapshot fixture was rejected by the independent verifier. Candidate hashes and native-bundle ELF/dependency checks also passed; they must not be substituted for the unproven original-service or desktop result.
