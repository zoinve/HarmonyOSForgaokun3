# Genuine SAMGR list query — 043

**No SA list was verified.** The genuine manager returned Binder status `1`; no token, policy or identity was changed to make the request succeed.

The request was copied from the successful unchanged SDK encoder test 042: transaction 5, flags 0, descriptor `ohos.samgr.accessToken`, argument 15, 64 bytes. Its SHA-256 is `068d40b750787291dfa20abd19f9a225b5373f54115915449d7ac919f1395ed0`. Original request serial evidence and proxy hash are recorded in the preparation manifest.

The observer ran as the policy-authorized init domain and verified enforcing mode. After original device initialization, it received 96 identical error replies from UID 5555: 4 bytes `01000000`, no embedded objects, flags 24 (`TF_STATUS_CODE` present), transport result 1. Early attempts also encountered an unlabeled Binder device and an absent manager. The bounded observer did not declare a successful list reply. The external VM observation ended at 60 seconds; full service and runtime readiness remain false.

This result does not yet distinguish an application authorization check from protocol/dispatch handling. Static original server analysis is the next step; status 1 is not relabeled as an empty list or a success.

Independent verification checked preparation artifacts/source, local versus WSL result and exact serial bytes, actual kernel, all three whole original images, the retained private scratch filesystem, and read-only drive/hardware/fstab/preservation guards. It independently rejected the reply before vector decoding. Serial SHA-256: `b894934253ddf6c1b4ea73e74264f0b263a162b2c97079e277bb2855bf21662e`.

Original init selected its unchanged SDK developer policy, as in the preceding genuine-init boots; this is not the separate manually loaded production-policy test. No original userdata, host network, GPU, physical boot or Ubuntu configuration change was involved. Repeated nonzero replies are retained in the raw evidence; further probes should stop rather than retry an already-received deterministic semantic error.
