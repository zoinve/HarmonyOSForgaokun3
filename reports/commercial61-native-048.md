# Commercial native 048 candidate

047 recovered logs establish original init and RenderService startup but do
not establish trace readiness or a normal target exit. This candidate persists
a snapshot before and after every tracefs control write to locate any failure
boundary. It does not assume a kernel panic or a particular probe failure.

Reuse the exact 047 kernel and matching hardware/ashmem module set. Original
inner bootstrap, services, desktop launch order, authentic Binder caller PID,
credentials, authentication and token checks remain unchanged. Keep target
SELinux support/policy and permissive mode, 150-second target and 270-second
outer deadlines, Ubuntu default/current boot, original images and manual entry,
screen-off timer and latest-two-experimental-entry retention.

No 046/047 operational boot is repeated. Candidate creation is not evidence
of native desktop pixels, interaction, probe attachment, or a failure cause.
