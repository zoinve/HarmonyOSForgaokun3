# Original init 038: hardware and original fstab contract

## Verified result

The original SDK init ran as PID 1 on the isolated ARM64 test kernel with `enforcing=1`. Its original hardware selector resolved `/vendor/etc/fstab.hmos.emulator`. Serial/capacity guards confirmed system=vda, vendor=vdb, sys_prod=vdc and fresh disposable data=vdd; no original userdata was attached.

The 60-second observation expired, rather than proving boot completion. Original SAMGR reached main at about 18.88 seconds and produced 38 registration log records. These are not 38 independently verified services. No previous token-lock/gettokenid failure messages were observed. Original init selected its own **developer policy**, not the production policy used in earlier standalone tests; enforcing AVC denials remained and were not bypassed.

No independently observed manager reply or desktop was established. `runtime_verified` and `services_ready` remain false. Missing hardware executables, service transitions and resource/data/sysfs access remain unresolved.

## Preservation and independent checks

`baremetal-sdk-original-init-qemu-038/independent-verification.json` verifies preparation hashes, generated C source, exact local/WSL result and serial equality, kernel, private scratch image, original image hashes, explicit enforcing/LSM arguments, hardware selector and read-only disk attachment contract.

- Serial SHA-256: `c6e3b96d12291f26862d545e26da216652affd388133a81210fe86708d6b2998`
- Test kernel SHA-256: `5968eea1728b4edd2a9bc898ef3c2fb39cf0e3ffbcb5f686b318c90be601604d`
- System image SHA-256: `19922349cf9550aea47c241efa42bfaae00060028e5db5c2445fc3796ba324d3`
- Vendor image SHA-256: `4e0c24992070e10cb35277faf8fda1e27241d455c677d58289a6bf0d75a0f8f7`
- Sys_prod image SHA-256: `41fa2bbc6862262cf1b87149b2218e019d385abc03599abc5f04155e11623b78`

All original images remained byte-identical. Only a fresh 512 MiB RAM-backed ext4 data image was writable. Its private evidence copy was retained after timeout; it may be unclean and is not to be repaired in place. No MateBook reboot, Ubuntu change, SDK image rewrite, policy exception or fabricated token was used.

## Next bounded check

039 retains this boot contract and adds a child observer. It waits for original init's policy load, requires the policy-authorized kernel-to-init transition and enforcing state, then sends genuine PING transactions to handle 0 without installing any manager. A reply would establish that endpoint's response only, not full service or desktop readiness. The original SDK's `BinderInvoker::PingService` contract is recorded in `baremetal-sdk-ping-contract039-audit.json`.
