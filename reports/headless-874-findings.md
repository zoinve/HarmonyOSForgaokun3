# Headless OOBE observation 874

- Sent one SIGTERM to exactly `com.huawei.hmos.hwstartupguide`, PID 6122, at guest second 150. Return value was 0; no other process was signalled.
- The system relaunched the same application as PID 14447 at second 153. SceneBoard PID 4758 remained present.
- `next-experiment/run-874/post-oobe.png` still shows a black OOBE screen with its blue next arrow, not a desktop.
- `hilog --help` established that this image uses `-z N` for tail length; `-t` selects log types. The attempted `-x -t 200` was invalid and produced no usable application logs despite returning zero.
- Next diagnostic payload 875 uses `hilog -x -z 300` and read-only process/thread snapshots. It does not stop OOBE or change identity, activation, permissions, services or watchdog protections.
- Original-image post-run integrity is reported by the runner separately; desktop success is not assumed.
- Read-only extraction/disassembly of the original system's `libtokensetproc_shared.z.so` shows ioctl constants `0x80084101`, `0x40084102`, `0x80084103`, `0x40084104`: its basic token API uses magic `A` (65), consistent with the reference driver. The repeated rejected magic `T` (84) therefore does not establish that the basic token API is mismatched. No token code or credentials were modified.
