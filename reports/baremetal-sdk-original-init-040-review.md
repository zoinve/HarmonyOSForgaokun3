# Original SDK init 040: genuine manager transport reply

## Verified result

The original SDK init booted as PID 1 with its own policy/bootstrap and original service configuration. The bounded observer received a real handle-zero Binder ping reply from UID 5555 (SAMGR), with transport result 0. It verified its `init` domain and SELinux enforcing state before querying and enforcing state again after success. The request flags and transport-success interpretation match the original SDK's `BinderInvoker::PingService` implementation.

The observer did not register a replacement manager, create or modify tokens, relabel devices, load a policy, or grant permissions. One early Binder mapping denial was treated as a bounded not-ready observation while original init completed device setup; the policy denial was not bypassed.

The independent verification in `baremetal-sdk-original-init-qemu-040/independent-verification.json` confirmed prepared files/source, the exact test kernel, all three complete original image hashes, the private generated scratch image, local/WSL results and byte-identical serial logs, and the original read-only disk/hardware contract. Serial SHA-256: `92317579108b08e5a0ff17e5a8b499975c5385dce973068eecce154b3b3a4522`.

## Scope and limits

- This is a bounded QEMU experiment, not a physical MateBook boot or HarmonyOS desktop.
- The original SDK selected its own developer policy; this must not be called the separate production-policy experiment. Actual queried domains remained enforcing; no policy was edited.
- A ping transport reply is not endpoint-token authentication, system-ability lookup success, permission-service correctness, or full-system readiness.
- The 60-second external observation timeout is not a readiness success. `runtime_verified` and `services_ready` remain false; the narrower manager-ping observation is true.
- Forty-one registration log records are observations, not 41 independently tested services. No old token-lock/initial-tokenization failure messages were observed; this is not exhaustive token-service validation.
- All original images, source/configuration preservation guards, and Ubuntu were preserved. Only a fresh private RAM-backed data image was writable. No original userdata, network, GPU, or physical host devices were attached.

Next: derive a concrete system-ability query from the original proxy and original parcel encoder, then observe the real manager's response without altering identities or policy.
