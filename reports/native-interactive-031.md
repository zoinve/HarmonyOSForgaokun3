# HarmonyOS 031 — Binder PID namespace repair candidate

Installed entry: **HarmonyOS 031 - Binder PID FIX - NO AUTO REBOOT** (`native-original-graphics-031.conf`). It was not selected or booted by this installation. Ubuntu remains the default; 030 is retained.

## Change

030 evidence proves that Settings' input socket uses inner PID 2751 while window routing uses outer PID 3120 (`NSpid: 3120 2751`). MMI cannot find the target and reports a window-state error, which leads SceneBoard to close the application. The input-method MainAbility follows the same failure chain.

The target kernel's extended Binder sender-information path incorrectly uses an outer numerical PID. 031 retains a reference to the real sender TGID for each transaction and translates it into the receiver PID namespace when delivering extended sender information. Both transaction-free paths release the reference, including error cleanup. This supports asynchronous transactions without substituting the standard sender field, which may legitimately be zero there.

Only independent copies of `drivers/android/binder.c` and `binder_internal.h` are patched. Tokens, UID/GID, standard Binder ABI, namespaces and permission/window-exception checks are unchanged. Userspace bootstrap is byte-identical to 030; only the outer run directory/labels differ. Continuous capture still uses filenames `interactive-hilog030.log` and `interactive-faults030.log` in the new `native-interactive-031-<bootuuid>` directory.

## Verified before handoff

- New ARM64 kernel compilation succeeded, release/configuration match the existing module set. All 9,718 previously exported built-in kernel symbols remain present. No module-version configuration was changed; the change is internal to Binder transactions.
- Source regression checks passed for namespace translation, real PID reference lifetime, normal/error cleanup, unchanged tokens/standard ABI and repeat-patch refusal.
- Nine candidate artifact hashes passed. Two actual native non-PID1 guard checks refused execution as intended.
- Installed kernel/initrd/DTB hashes independently match the manifest. Kernel SHA256: `6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5`.
- 90 other existing EFI files remained unchanged. Only the unreferenced old 021 EFI initrd duplicate was reclaimed after comparison with its retained staged original and a pre-deletion journal; original staging/evidence remains.
- The repaired kernel has its own `/native-original-graphics-031/linux` path. Shared 015 kernel, 030 entry, Ubuntu default, firmware entries and active automatic screen-off timer were preserved. No one-shot selection or reboot was requested. EFI free space after installation: 72,691,712 bytes.

## Runtime acceptance still pending

The compiled repair is installed, but **application behavior under the new kernel has not yet been verified**. Manually select 031, open Settings and the Xiaoyi input-method application, and leave each window open beyond its previous failure interval. Wait at least 15 seconds after any failure before returning to Ubuntu, then retrieve the new continuous logs. Confirm that socket registration and window routing agree on the actual inner PID and that MMI no longer requests the observed window-state close.

031 retains manual indefinite operation, `panic=0` and no diagnostic automatic reboot or synthetic input. Original service critical-failure checks are not disabled. Hardware resets and unrelated application faults are not ruled out. Application data remains volatile RAM; only bounded exported evidence is persisted. Do not overwrite prior 030 recovery evidence or reuse completed numbered trial records.
