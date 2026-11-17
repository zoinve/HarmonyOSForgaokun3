# Native 167: persistence proved, pre-init log collision found

One bounded boot, no retry: commercial61-native-087-61950145-5809-4403-9c56-c820c3390a07.
Start 2026-11-16 07:22:21 UTC; Ubuntu returned 07:23:33 UTC.
No authenticated native connection or original-init handoff occurred.

The disk file, loop inode and exclusive lock checks passed. Runtime166 mounted
the persistent filesystem and read the prior native boot ID
054d8bc8-bc93-407a-ab6c-85b00eb7658c. It archived the five adaptation-owned graphics
objects before committing its own boot marker. This is a real cross-boot data
read, not a fresh seed or synthetic fixture.

The next operation failed: NATIVE_ORIGINAL001_FAIL memory prerequisite evidence
108 errno=17. commercial-memmgr-prerequisites-108.h uses O_CREAT|O_EXCL for
/data/commercial-memmgr108.log. This sixth adaptation-owned diagnostic object was
not included in the original five-object archive. Do not reset data, modify
service identities, or infer a filesystem corruption/activation failure.

Both nested filesystem and backing-file flushes succeeded. Read-only offline
e2fsck passed, the filesystem was clean, the new marker matched native167 and
all five previous objects were found in its history directory. SceneBoard's
installed directory was present. Data occupied 3,348,193,280 bytes of the 8 GiB
image; insufficient space is not the cause.

The normal retrieval refused an absent identity-probe log, correctly. A first
partial retrieval also refused because the wrapper child had started. The
distinct pre-handoff retrieval required absence of original-init handoff and
identity-probe markers before allowing that log to be absent; physical-serial
scanning remained enabled. All 118 exported files matched remote hashes.

Post-return checks preserved original images, firmware, Ubuntu default/current,
enabled/active screen-off timer and an unmounted LAB partition. Latest entries
are 166/167; archived164's shared payloads and the original seed remain intact.
Ubuntu boot ID: af8470ff-1887-4377-acc1-cad63abc35d9.

Candidate168 adds only the missing memory-log history operation before invoking
the unchanged original memory prerequisites. Overall storage/desktop acceptance
remains incomplete until full original-service boots succeed with retained data.
