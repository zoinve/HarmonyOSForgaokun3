# Original samgr ping 030 — failed, not service-ready

The bounded domain-execution probe in 029 was insufficient to establish Binder readiness. Trial 030 added a real `PING_TRANSACTION` to handle 0 on the actual kernel Binder device, without installing a substitute context manager.

The original samgr executable entered `u:r:samgr:s0` with UID/GID 5555, but the kernel returned a dead/failed transaction response, recorded as `received=1 result=-2`. The current probe combines those two response types; it does not yet distinguish their exact cause. The runner correctly recorded `runtime_verified=false`. The guest terminated samgr after observation; its status 15 is not an independent crash.

Original production policy remained enforcing. Earlier policy, token/Binder device ABI and read-only filesystem checks passed. Expected policy denials remained visible, including samgr CPU sysfs directory reads and console ioctl `0x5413`; no rules were relaxed.

The entire original system image retained SHA-256 `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`. The test kernel, configuration and guarded native source files also remained unchanged. No physical reboot or Ubuntu modification occurred.

Trial 031 adds bounded `/proc` wait-point, thread and mapping observations before the same mandatory ping. It does not extend the service observation window, change identity, replace libraries or weaken the success criterion. Its results are pending at the time of this note.
