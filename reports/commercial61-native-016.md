# Commercial 016: aborted before original init

The single 016 attempt returned to Ubuntu after approximately 48 seconds. This
was a bootstrap failure, **not** a commercial desktop or GPU runtime result.
The genuine DRM nodes were created, then hardware-file copying failed with
`commercial observer copy open errno=2`. Both continuous service logs are empty;
the commercial init and graphics services were not executed in this attempt.

The archive contained the hardware files but omitted thirteen parent directory
entries. Linux initramfs extraction does not create missing parents recursively.
Byte/hash equality checks alone had failed to test this extraction requirement.
017 adds explicit directory entries; the 016-r2 bootstrap and hardware files
remain unchanged. The failed first compile directory and successful r2 build,
as well as all 46 hash-verified runtime evidence files, remain preserved.

Evidence: `commercial61-native-016-r2/runtime-evidence/`.
No original commercial images were written, no SDK userland was substituted,
and Ubuntu default boot and the disabled screen-off timer were preserved.
