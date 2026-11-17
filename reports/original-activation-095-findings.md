# Native activation: observed local TEE transport gap

## Evidence

`original-activation-095.json` reads preserved 092 logs, not reference-project
runtime. `original-tee-interface-095.json` records a separate read-only audit of
original image clients and the current target's kernel/device metadata.
No boot, device-node opening, secure firmware call, certificate read, or write
to any original image/security store occurred in either audit.

The original `teecd` (SHA-256
`117802a0325168494f2191b0cea3d593ff7d2821a97f33c09c17084f0baf7e7f`)
contains literal device paths `/dev/tc_ns_client` and `/dev/tc_private`.
The current Ubuntu device metadata has neither node nor any matching tee/tz/qsee
character node. `/boot/config-7.1.0-rc3-gaokun3-el2+`, corresponding to the native
trial kernel release, records `# CONFIG_TEE is not set`; current Ubuntu's
configuration does too. QCOM_SCM, QCOM_TZMEM and QCOM_QSEECOM are enabled, and
qcom_qseecom/uefisecapp drivers exist. This alone does not establish compatibility
with the original client's required device ABI or signed trusted applications.

## Actual 092 Failures

- Early original `teecd`: `Failed to open dev node: 2`, then `open tee client
  dev failed`, filesystem/misc agent initialization failures.
- Original `cadaemon`: `open tzdriver fd failed`, then context initialization
  failure. These occur before the late activation attempt.
- DCM PID 16245 later repeatedly logs `connect() failed, errno=111`.
- At 2026-11-15 16:13:43.701 target log time, DCM records 51 CA-daemon connection
  failures, `initialize context: failed:0xffff0000`, and
  `OpenSession[77]: TEEC initial failed ffff0000`.
- The original HDI path then records failed TA command 9/certificate-state
  retrieval, service result -65536, and failed certificate activation attempt.
- The same run also contains `GetDevUdidData: Failed to get device udid`.

Thus this is not presently demonstrated to be merely a network/server rejection.
The logs demonstrate failed local transport/context setup, but not a successful
TA execution followed by a missing/rejected device certificate. They do not prove
whether the required compatible trusted application or accepted credentials exist
on this hardware. 094 early identity success is still unproven after interruption.

## Engineering Direction

Activation requires investigation of a genuine compatible client/kernel/firmware
path, not a fake `/dev` alias, success stub, borrowed identity, or fabricated
certificate. Enabling generic TEE configuration alone does not prove the two
original device interfaces or trusted application are implemented.

Keep desktop progress separate: native normal-window-close behavior remains an
untested avenue, while repeated force-stop is already disproven by 078. The new
`native-normal-close-095.c` source is not installed or runtime-validated and must
not be described as an executed experiment.
