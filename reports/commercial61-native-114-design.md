# OOBE comparison 114: one SceneBoard startup owner

## Hypothesis and limits

Completed 099 retained both the inherited early account/Home bridge and the
reference script's later SceneBoard start request. The second request is an
unresolved integration difference, not a proven cause of guide recovery.
114 tests only this difference. It does not extend into kernel adaptation.

## Exact change

Parent: completed 109. Only archive member
native-target/harmonymac-reference099.sh changes. Replace its SceneBoard aa
start with a guard requiring the existing SceneBoard process. The early
desktop-order020.sh script remains byte-identical, including its genuine
account service retries and normal Home start path. Its own existing bounded
launch retries remain; this candidate removes a second startup owner, not
every possible repeat request within the early path.

Original guide wait, ten-second sleep, and single aa force-stop remain.
Original recovery, setup state, identity, authentication, original binaries,
kernel and images are unchanged. There is no repeated guide-kill loop.

## Preboot checks

Six offline script tests passed, as did three isolation guards (exit 77).
Full ordered-overlay reconstruction equals the full candidate archive.
The actual runtime remains byte-identical at its existing 108 path, and
installation verifies that remote path's hash explicitly.
Installed overlay SHA256:
3fd1f250b8af4232cfca433614808d16ca6cb81597ce56c620334d6af51c086b.
Entry retention archive: boot-entry-retention-20261115T174217722577Z.
Current experimental entry files: 109 and 114. Shared payloads retained.

## Evaluation

Exactly one bounded diagnostic boot, then serial read-only noload retrieval
and preservation verification. Check the new existing-process guard marker,
the force-stop result, original guide death/recovery and focus samples.
If guide recovery remains, removing this second startup request was not
sufficient. READY, process absence and CLI success do not establish desktop
success. Real native desktop acceptance still requires full-resolution
pixels, stable desktop behavior and a visible response to real interaction.
