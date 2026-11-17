# Share and kernel checkpoint 519

Date: 2026-11-17. Supersedes the current-state statements in checkpoint496;
historical evidence is unchanged.

## Published baseline

The requested source-only GitHub checkpoint was pushed to main as b7bad42.
Original installation images, runtime binaries, private configuration and raw
device logs remain local.

## Native experiment502

Candidate502 booted once with kernel490 and its matching rebuilt module bundle500.
Ubuntu was observed again at 03:53:08 UTC. The post-return guard511 verified the
Ubuntu current/default entry, absence of a one-shot entry, active screen-off timer
and unmounted lab partition. No filesystem validation suite was run.

Nineteen runtime evidence files were retrieved with transfer integrity checked.
Analysis509 found a real p2p0 interface creation result of zero, but all three
control PING attempts failed with ENOENT. Huawei Share remains unaccepted.
The supplicant command's zero exit status did not establish a running daemon.

The real pmic_resin input device was enumerated. Physical volume-down delivery
and HarmonyOS volume changes are not yet verified. Memory-cgroup enforcement,
Linux compatibility-platform application execution and Task Manager frequency
display are also not accepted merely from this boot or the kernel configuration.

Read-only inspection512 of data197 found neither selected P2P log. No raw
credentials or peer identifiers were exported; active data165 was not accessed.

## Confirmed startup defect and correction

The P2P-only supplicant499 lacked CONFIG_DEBUG_FILE while its launch command
specified -f. Upstream's unsupported-option path prints usage and exits zero.
QEMU option-parser regression516 reproduced this behavior without opening a
radio. Its corrected build515 accepts -f and prints the requested version
instead of usage. The older usage page also contains a version banner, so a
version substring alone is not a sufficient assertion.

Candidate517 packages the corrected binary, retaining the existing kernel/module
and driver integration. It has not been installed or booted at this checkpoint.
Real PONG, original bridge attachment, group handshake and a physical file
transfer remain required. Ordinary wlan and original service authentication
are not replaced; no connection events or hardware readings are fabricated.

## Local evidence

- reports/commercial61-native-502/share-kernel-analysis-509.json
- reports/commercial61-native-502/post-return-guard-511.json
- reports/commercial61-native-502/share-data-analysis-512.json
- reports/share-supplicant-515/result.json
- reports/share-cli-516.json

The source builds depend on retained local inputs and are not self-contained
redistributable system images. Desktop173 and Ubuntu default remain protected.
