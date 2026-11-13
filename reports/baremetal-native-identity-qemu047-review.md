# Legacy Binder and initial enforcing read probe (047)

The unchanged profile003 console test kernel passed both diskless QEMU cases: real legacy `/dev/binder` protocol 8/features 5, active SELinux with initial enforcing=1, and missing diagnostic opt-in refused with exit 77 before the probe creates its mountpoint. Both cases leave no probe mountpoint behind.

The helper only reads token/Binder identities and a private read-only SELinuxfs mount. It does not set identities, register a Binder manager, load policy, or change enforcement. Thus this is **not** evidence of loaded-policy authorization, transactions, physical-board compatibility, or a HarmonyOS desktop.

`reports/baremetal-native-identity-qemu-047/independent-verification.json` independently checks the two binaries and sources, both raw serial logs against WSL copies and recorded SHA-256, the kernel and both native/test configurations. Native and test configurations and critical source hashes remain unchanged. No disks or network devices were attached; nothing was installed or rebooted on the MateBook.

Helper SHA-256: `3aa3890222f8448ff1e8feef5e101f378e20449cebfd247a83c684b2e438dd31`.

Next preparation: fresh diagnostic009, preserving the prior display/touch module plan and budget, with only the helper path changed. Any board entry must use the profile003 native kernel and explicitly include `enforcing=1`; the QEMU-only console kernel must never be substituted.
