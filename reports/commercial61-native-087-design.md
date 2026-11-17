# Original product workspace 087

Goal remains a stable, visible and interactive native desktop, not merely a
successful configuration read. This candidate tests whether unavailable default
Dock apps contribute to SceneBoard freeze/relaunch and startup-guide disruption.

Use the original external workspace interface at
/system/etc/hw_launcher_default_workspace.json, in the existing RAM-backed
read-only system overlay. Preserve original layout dimensions; supply a nonempty
Dock entry for the genuinely installed browser (entry/MainAbility). Do not modify
the signed SceneBoard HAP, application registration, provisioning state, native
service identity, permissions, watchdogs, authentication or network helpers.
Omitting unavailable default shortcuts is a board-configuration experiment, not
a claim of successful activation or a permanently complete desktop feature set.

The only additional ESP archive member is init. It loads the independently
compiled own bootstrap from the existing read-only/noload Ubuntu mount, verifies
its source hash, copies it into the target RAM tree, verifies the destination
hash, and refuses handoff on failure. The sidecar remains outside the ESP.
All four images and the original init/services remain unchanged. The archived
bootstrap stays byte-identical; its replacement exists only in test RAM.

Require static admission, measured overlay fit above the existing 32 MiB guard,
normal-context refusal from all own executables, Ubuntu current/default and timer
guards, unique 087 evidence, a single bounded boot, and serial retrieval followed
by preservation verification. Retain latest entries 086/087 and archive old entry
contents/hashes before removal, preserving shared payloads.

Judge runtime by original config-loader logs, absence/presence of BMS freeze,
SceneBoard lifecycle, real network validation, complete full-resolution frames
and actual interaction. A loaded workspace, nonblack frame or initialized Dock
alone is insufficient. Original uitest permission refusal is not bypassed.
