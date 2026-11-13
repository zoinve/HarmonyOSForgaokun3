# Original samgr wait points 031

Trial 031 retained the failed real-manager ping and added bounded process observations. It did not change policy, identity, libraries or the observation duration. The runner still reports failure.

The main samgr thread was running (`State: R`, `wchan=0`, sampled syscall `running`), not sleeping in a Binder read. Other threads included an epoll waiter and two genuine kernel `binder_thread_read` waiters on FD 8. A read-only Binder mapping was present. This establishes that some original IPC initialization occurred, but does not establish context-manager registration or explain the failed ping.

Process credentials remained UID/GID 5555 with supplementary groups 1000, 1065, 3009 and 5555. Policy denials remained enforcing. The initial mappings read was a bounded single read, not a complete library inventory; repeated missing-HiLog-server messages were preserved in the raw serial log.

Read-only disassembly of the original samgr entry sequence resolved its main function to `0x4ad1c`. Its normal path calls the original `IPCSkeleton::SetContextObject` and later `JoinWorkThread`; this is static control-flow evidence, not proof that either call was reached in trial 031. See `baremetal-sdk-samgr-main-audit-001.json`.

Trial 032 adds kernel Binder state/log observations and distinguishes `BR_DEAD_REPLY` from `BR_FAILED_REPLY`. No substitute manager, invented token or permission exception is used. Results are pending when this note is written.
