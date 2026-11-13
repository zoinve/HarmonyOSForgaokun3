# 031: Binder sender PID namespace repair

## Evidence and scope

Recovered 030 logs show Settings registering its input socket as PID 2751 while window routing uses PID 3120. The retained original process status proves `NSpid: 3120 2751`: these are the same process in the outer and target PID namespaces. MMI fails to find the routing PID, reports a window-state exception, and SceneBoard closes the UI ability. Both Settings and the input-method MainAbility exhibit this shared close chain.

The matching kernel's standard Binder sender PID already translates into the receiver namespace. Its `CONFIG_ACCESS_TOKENID` extension instead stores `t->from_pid`, an outer numerical PID, in the extended sender information consumed by the SDK.

## Repair

Retain a reference to the actual sender TGID (`get_task_pid`, not a guessed number) in each extended Binder transaction. At delivery translate that reference through the receiver's active PID namespace. Release it on both normal and error transaction-free paths. This also retains identity through asynchronous delivery, where the standard Binder sender field may be zero.

Token values, credentials, UID/GID, namespaces, standard Binder ABI and all existing permission/window-failure checks remain unchanged. No caller identity is fabricated and no window-exception handling is suppressed.

## Candidate and verification boundary

031 uses an independently compiled kernel and its own EFI kernel path. It retains 030 userspace, continuous bounded capture, manual startup and no automatic reboot. The original kernel, 030 entry and prior evidence are retained; Ubuntu remains the default.

Source regression checks cover the receiver translation, reference capture/release paths, unchanged token/standard Binder fields and repeat-patch refusal. Compiled-image, configuration, release and kernel-export checks must pass before installation. These checks are not proof that both applications now work: opening Settings and the input-method UI in the new kernel and examining their continued input/window routing remains the required runtime acceptance test.
