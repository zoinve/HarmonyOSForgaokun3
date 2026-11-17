# Storage fixture 160: no native-boot root cause inferred

After native 159 completed and preservation verification passed, an independent
native ARM64 Ubuntu fixture ran the exact bind_log159/key_copy159 function bodies
inside a new mount/PID namespace under a 15-second timeout. Only the fixture root
and on-device key-source prefix differed. Synthetic logs were used exclusively.

Both binds and the RAM-only key copy returned zero. Opening the bound log for
writing failed with EROFS, while appending through the existing source descriptor
was visible to the read-only destination. No key bytes or raw HarmonyOS logs
were exported. The generated C/function/binary hashes are recorded in
live-debug-storage-fixture-160/result.json.

Outer mountinfo and boot ID were unchanged; the private tmpfs root disappeared
on namespace exit, leaving an empty persistent mountpoint. Original key inode,
mode, ownership, size, mtime and ctime were unchanged. Access time is intentionally
excluded from the metadata comparison because this is a legitimate on-device
read. Ubuntu boot ID remains e5478e6f-48ca-4fc1-a0ee-aa170b3f8351.

This does not establish which native 159 substep failed, nor does it establish a
HarmonyOS SSH connection. Do not change file permissions or guess a key failure.
The next diagnostic must expose fixed stage/errno records for source-FD metadata,
destination metadata, bind/remount/statvfs and key open/read/write separately.
live-debug-storage-161.h implements those fixed records without private data;
it is not yet integrated into a built or booted native candidate.
