# Original samgr loader-path repair, experiment 028

This is a bounded executable/domain observation, **not a ready system service**.

The original image contains an `/etc -> /system/etc` symlink. The previous RAM guest omitted it, hiding the original musl search-path and namespace configuration. Experiment 028 adds that one RAM symlink; it does not replace libraries, set a substitute library path, or alter the production policy.

## Observed result

- Original samgr executes with `u:r:samgr:s0`, UID/GID 5555 and its configured supplementary groups.
- The previous 22 missing shared-library errors disappear.
- The process then aborts with `random_device failed to open /dev/urandom: No such file or directory`; raw wait status is 6 (SIGABRT).
- The enclosing identity, enforcing-policy and read-only filesystem checks pass. `runtime_verified` refers to that bounded scope; `services_ready` and `services_tested` remain false.

Evidence: `baremetal-selinux-qemu-028/result.json` and the unmodified serial log. The log also retains missing-HiLog-server messages; those are not treated as successful initialization.

Independent verification additionally checked both prepared files, actual kernel and whole original image hashes, and byte-identical local/WSL logs and results. Serial SHA-256: `07b7baff3a83b9fd42e0a5caa97e01edfba4332af3baeefb21b175130d29c320`. It explicitly confirmed the SIGABRT/random-device failure rather than misreporting service readiness.

## Preservation and next test

The original system image remains read-only, with whole-image SHA-256 `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3` unchanged across execution. Kernel/configuration and critical sources are unchanged. No physical-machine reboot, network, display activation, host mount or SDK image write occurred.

The next isolated test supplies the **real kernel** urandom device (major 1, minor 9), mode 0666 and `u:object_r:dev_random_file:s0`, as specified by the original SDK. It must not substitute deterministic bytes, fabricate identities or weaken SELinux.
