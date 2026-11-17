# Native 123: Reference-Style Local First-Run Seed

The user explicitly authorized proceeding at the agent's discretion after the
new HarmonyMac method was explained. Only the two local first-run flags change
on a reversible, RAM-used development seed; commercial activation, identity,
authentication, original HAPs and recovery remain untouched.

Source is the original services' 121 private data snapshot, schema inspected
in 122. Each SQLite readonly connection backs up all committed data including
WAL to a new offline checkpointed DB. The exact upstream helper at commit
ed213a08817c642e9b455fb7d8f5271da41631eb prepares new main/slave files:
device_provisioned=1 and user_setup_complete=1 for user 100.

Original schema, unrelated rows, UID 20002, GID 3012, mode 0660, POSIX ACL,
user.security where present and SELinux labels are verified preserved. New
databases and actual ancestor-directory metadata are placed into the exact
original 512 MiB blank scratch filesystem. No old SceneBoard preference cache,
unrelated data, stale WAL/DWR/compare/binlog or fabricated framework table is
included. All original sidecars remain in the immutable private snapshot.

Prepared seed SHA256:
02c810f94799cf4b89cc59dea2409981b4678e8b201d60c0ceb62fd7397b21cd.
It passed e2fsck -fn with exit 0. The seed stays private on target Ubuntu and
is only copied to the RAM scratch path after boot-time hash verification.
The unchanged original runtime then performs its normal 8 GiB data expansion.

Executable behavior starts from exact 116, dropping 121's one-time capture
instrumentation. Only init and its integrity wrapper differ in the archive.
All other runtime/service/startup/recovery/reference scripts remain unchanged.
The inherited original guide-wait helper may wait beyond this boot's target
budget if no guide starts; absent reference samples must not be interpreted
as proof of absence. Use original state logs, full captures and actual input
evidence, and improve observation separately if required.

Acceptance is not two changed keys or process absence: verify actual original
setup reads, original OOBE behavior and real full-resolution desktop plus
visible interaction. Keep Ubuntu default, one bounded boot, active display
timer, immutable images, original manual entry and latest-two entry retention.
