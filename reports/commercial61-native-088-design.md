# SceneBoard canonical config view 088

Goal remains the stable interactive original desktop with full-resolution pixel
and interaction evidence. 087 created the workspace but original configuration
discovery returned no paths and retained 12 presets, followed by SceneBoard freeze.

The actual packaged appdata-sandbox019 configuration already aliases
/system/lib64 to /usr/system/lib64, not /system/etc to /usr/system/etc. Therefore
a /usr/system symlink would conflict with an existing directory. Add only a
SceneBoard-specific recursive bind of already-exposed /system/etc to its
canonical /usr/system/etc name, using the original appspawn individual mount
configuration. Preserve common mounts, all other apps, GIDs, permissions,
sandbox switches, service identities and original application binaries.

This is an additional name for already-visible configuration, not exposure of
Ubuntu's /usr or another host tree. The original browser-only workspace candidate
and dimensions remain unchanged. No activation/provisioning state is modified.

Only two text members change: appdata-sandbox019.json and the own layout
diagnostic script. Read the actual policy parameter and at 60/100/130s collect
bounded stat/hash observations for both workspace paths through the real
SceneBoard process root. Retain original UITest attempts and their actual exits;
do not bypass accessibility permission checks or infer layouts from timeouts.

The 087 executable core and its hash-pinned RAM bootstrap remain byte-identical.
Thus the new 088 boot entry uses inherited COMMERCIAL087 core labels and creates
a fresh commercial61-native-087-<boot-id> evidence directory. This is a different
configuration experiment, not a rerun of 087: keep entry 088, own CONFIG088
markers, report directory 088 and exact overlay hash authoritative. Retrieval
must exclude the already-recorded 087 run and require exactly one fresh run;
do not relabel or overwrite historical raw evidence. Preserve the external
087 bootstrap dependency and all previous payloads. The tiny two-text-member
overlay must fit above the existing 32 MiB ESP guard.

Require exact-change tests, all normal-execution refusal guards, a unique single
bounded boot, retention of entries 087/088, serial retrieval then preservation
verification, original callback/lifecycle evidence and complete frames. Config
consumption and Dock completion alone do not establish the full goal.
