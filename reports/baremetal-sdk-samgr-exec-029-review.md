# Original samgr with genuine urandom, experiment 029

The RAM guest now supplies kernel character device 1:9 at `/dev/urandom`, mode 0666, root:root, labelled `u:object_r:dev_random_file:s0`. The preparer verifies the mode and label against the original SDK configuration. No random bytes, identities or authorization results are fabricated.

The unchanged original samgr executes in `u:r:samgr:s0` with UID/GID 5555. Missing-library and `random_device` failures seen in previous fixtures disappear. It remains alive through the bounded observation window, then the test stops it with SIGTERM (raw wait status 15).

This proves neither Binder readiness nor complete service initialization. Both `services_ready` and `services_tested` remain false. Experiment 030 separately adds a bounded, nonblocking ping to the genuine Binder context manager; the probe must not register a substitute manager.

The original production policy remains enforcing. The serial log retains expected negative-test AVCs, missing HiLog-server messages, and samgr CPU-directory/console-ioctl denials; none were bypassed. Existing ABI and read-only filesystem checks pass.

Evidence: `baremetal-selinux-qemu-029/result.json` and unmodified `serial.log`. Whole original system-image SHA-256 remains `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`. Kernel/configuration and critical source preservation checks pass. There was no physical-machine reboot, network, display activation, host mount or SDK image write.

Independent verification confirmed both prepared artifact hashes/sizes, actual kernel and whole-image hashes, byte-identical local/WSL results and serial logs, and the bounded SIGTERM stop without the previous loader/random-device failures. Serial SHA-256: `f51e43a0d247f4b4644da17f33ddad09846cbf1c5dc36db50861f8b45c2840cf`. This verification still does not assert service readiness.
