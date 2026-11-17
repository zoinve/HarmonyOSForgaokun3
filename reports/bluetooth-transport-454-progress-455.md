# Bluetooth Transport454

Date:2026-11-17, Asia/Shanghai. Full driver goal remains active/incomplete.
Previous turn completed one438 target boot/retrieval. This turn made a concrete
transport repair and reproduced the old failure in local socket fixtures.

## Reproducible Defects

The original022 broker (retained in435/438) checks POLLHUP before POLLIN and
exits without consuming bytes already queued by a closing client.452 creates
real UNIX stream/SEQPACKET pairs, queues two distinct complete H4 packets,
closes the stream peer, and verifies simultaneous POLLIN/POLLHUP. Old435 fails
at the assertion that the controller peer received the queued first packet.
This is local transport evidence, not a demonstrated cause of missing physical
pairing on438. No Classic search/pair request was captured in that run.

The HCI datagram send and both receive calls also treat EINTR as disconnection.
451 retries only interrupted syscalls; it never retries a short datagram as a
second packet. It processes readable bytes before terminal flags and lets EOF
finish the client stream. Existing H4 framing, security, namespace, endpoint,
channel ownership and435 passive observations remain unchanged. No HCI command,
address/privacy selection, completion/status or key material is translated.

## Tests And Candidate

453 passed GCC address/undefined sanitizers and strict warnings. Fixtures cover
buffered full close, command fragmentation, coalesced command+ACL packets,
unchanged bidirectional bytes, stream half-close and interrupted poll/send/recv
in both traffic directions. Each injected syscall interruption was counted.
The old435 regression is explicitly checked for the receive assertion failure;
core dumps are disabled for that expected failed local child. Tests have a
bounded alarm/process timeout and access no HCI controller or target device.
Static ARM64 broker compilation passed.

454 built successfully, inheriting438 audio reconnect/playback/jack/touch and
original-service integration and replacing only the broker with451. Build
artifacts reside at /home/zoinve/harmony-virgl-883/commercial61-native-454;
manifests at reports/commercial61-native-454. It is uninstalled/unbooted.
No target reboot, image/data write or disk validation suite ran this turn.
Frozen438 evidence and existing entries173/438 remain unchanged.

Low-power operations remain truthful ENOTSUP; this transport repair does not
implement UART sleep/wake control. Bluetooth physical pairing/reconnection,
multitouch/app gestures, acoustics/mic and actual120Hz remain pending.
Next target test must be a new candidate attempt with essential preservation
guards and all prior retrieval exclusions through438. Do not repeat438.
