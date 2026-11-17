# Commercial image 019 — original application-filter path discovery

## Scope and evidence

018 recovered the original AppSpawn service. Its children stopped before application execution with `get filter name failed`, followed by failure to apply the original seccomp filter. The original commercial libraries and 17 filter files are present. Actual `libseccomp.z.so` disassembly places this error in `GetCfgFiles` path selection, before `dlopen` or the kernel filter syscall.

The original configuration layer searches `/usr/system`, while the original application sandbox exposes `/system/lib64`. 019 adds **one required bind alias** from the already granted `/system/lib64` to `/usr/system/lib64`. It changes no existing mounts, filter contents, service credentials, application permissions or sandbox switches. It does not disable seccomp, fabricate application identities, register fake services, or introduce SDK userland.

Offline tests used the actual commercial JSON and original filter: the alias resolves to the same inode, remains read-only, is readable inside a private chroot, and exposes no unrelated `/usr/system/etc`. The actual AppSpawn mount routine creates parent directories. This proves path behavior, not successful application-filter loading on the target.

## Candidate

- Original ISO: `L410-HarmonyOS-Installer-20261029.iso`; its original metadata is 6.0.0.110/API 20.
- Original system/vendor/sys_prod/chip_prod images remain read-only.
- Retains the verified commercial-runtime FD690 hardware backends, original AppSpawn executable and exact original application arguments.
- Retains 8 GiB volatile test data with memory admission, 90-second target budget, independent 210-second deadline and bounded final evidence flushing. Software deadlines cannot recover every kernel or hardware lock.
- Ordered initramfs chain: commercial 001 base, 017 parent-directory archive, 016 hardware archive, then the new 019 overlay.
- Overlay: 703,455 bytes, SHA256 `6f51708d76853330ef3750064f3b67b4aaba9e159d45941038bc907ee920e23a`.
- Installation preserved 116 existing EFI files, Ubuntu default, firmware entries, the manual GPU entry, and the disabled screen-off timer. No old files were deleted. The new small archive uses an explicitly reduced **30 MiB** EFI reserve; 31,830,016 bytes remained after installation.

## Runtime status

The single 019 attempt completed on 2026-11-13 (12:36:19–12:38:46 UTC), returning to Ubuntu boot `94f66c9e-87c7-41af-8c14-fcffe9baf5ee`. The target's configured timeout and termination were captured. Network return alone is not treated as proof of every cleanup step.

All 59 exported files matched their remote hashes after read-only, `noload` retrieval; the original LAB partition was unmounted afterward. Original filter-name and application-filter errors are now **zero**, and original AppSpawn created application children with result 0. SceneBoard installation succeeded, but its process was not observed. All three actual 160×256 scanouts remain fully black. **The desktop is not working yet.**

Further original logs show a startup ordering cycle: account 100 is created and its real key is unlocked, but activation rolls back when Ability Manager cannot find SceneBoard. The provided account-order script waits for account activation before attempting to launch SceneBoard. Account creation, authentication and signature warnings must not be bypassed to conceal this ordering problem.

Post-return checks verified all four commercial image hashes, Ubuntu default, firmware, manual GPU entry and disabled/inactive screen-off timer. Of 116 prior EFI files, only the boot-managed random seed changed. An initial preservation check raced with our read-only retrieval mount; it was retried only after retrieval unmounted the partition, without repeating the operational test. Both the coordination note and successful verification are preserved.

All prior numbered trials and their evidence remain unchanged. Current build and installation records are under `reports/commercial61-native-019/`.
