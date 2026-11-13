# Original samgr startup: 032

032 failed its required genuine context-manager ping. The precise returned event was `BR_DEAD_REPLY` (`0x7205`), not `BR_FAILED_REPLY`. A registered, responsive service manager has not been demonstrated.

The actual production SELinux policy denied init reads of Binder debugfs state, statistics and transaction logs. Those denials were retained; no policy exception or alternate context was introduced. Existing policy-load, enforcing-mode, device-ABI and original read-only filesystem checks passed before the service-readiness failure.

The original system image remained byte-identical (`19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`). The storage-test kernel, configuration and guarded source files remained unchanged. No MateBook reboot, installation or network device was involved.

## Next diagnostic

The unchanged production binary policy explicitly permits init to ptrace samgr (`baremetal-sdk-policy-trace-001.json`). 033 therefore adds bounded register/stack reads of the direct child, with temporary attach/stop/detach, without writing its memory or changing policy. Reads may still fail at other kernel checks; such failures will be reported, not bypassed. The mandatory real ping remains the readiness gate.

The additional disassembly in `baremetal-sdk-samgr-pre-registration001.json` is static evidence only. It does not identify the live instruction pointer. Earlier observations showed an active main thread and two Binder-reading worker threads, not successful context-manager registration.

Independent verification subsequently checked both prepared files' sizes and SHA-256 values, the actual test kernel, the whole original system image, and byte-identical local/WSL result and serial records. It confirmed the exact dead-reply event and preserved readiness failure. Serial SHA-256: `70f1e02ee24879deb799a04f2e6e67f28b9c4f2c466b347000c73fb4e401e2ac`. See `baremetal-selinux-qemu-032/independent-verification.json`.
