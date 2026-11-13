# Original init 039: observer began before Binder relabel

The original boot contract, original init, kernel and policies were unchanged. The bounded child observer successfully observed policy loading, entered `u:r:init:s0` through the policy-authorized transition and read enforcing state as 1. It did not register a manager, modify tokens or load its own policy.

At 1.75 seconds it attempted Binder mmap before original init had finished device setup. The actual AVC states:

```
denied { map } ... path="/dev/binder" ... scontext=u:r:init:s0 tcontext=u:object_r:tmpfs:s0 tclass=chr_file permissive=0
```

`ORIGINAL_INIT039_OBSERVER_FAIL bounded Binder caller mapping errno=13` followed. This is an observer preparation failure, not evidence that the genuine manager rejected a PING. `genuine_manager_ping_under_enforcing_policy_observed=false`, `observer_failure_observed=true`, `runtime_verified=false` and `services_ready=false` are preserved.

The overall observation reached its 60-second external bound. All three original image hashes, kernel/config, native configuration and critical source preservation checks remained true. Only a fresh private 512 MiB ext4 scratch data image was writable; original userdata was not attached. Serial SHA-256: `37444987470e3e3d45eef1b3b61048329876d646a7bc29fb335403af8282ab28`.

The read-only production-policy audit `baremetal-sdk-policy-binder-map-040.json` confirms init may map `dev_binder_file` but not a generic `tmpfs` character node. This is supporting static evidence, not a claim that the SDK-selected developer policy is the production policy.

040 changes only observer admission: missing/inaccessible device open or mmap returns a not-ready observation and closes its own descriptor. The existing deadline bounds retries. It never relabels the device or weakens policy; other protocol failures still fail. A successful genuine reply, if obtained, remains distinct from full service or desktop readiness.
