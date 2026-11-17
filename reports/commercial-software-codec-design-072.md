# Real Software Codec Backend 072

## Reference Reconciliation

The L410 adaptation implements a real IPC backend, not an in-process portable
decoder: `video-h264/fcodec_h264_bridge.c` and
`video-hevc/hevcdec_kylin_proxy.c` send complete access units over Unix
SOCK_SEQPACKET sockets, passing input/output memfds with SCM_RIGHTS. Its helper
opens Kylin `h264_omx_dec` / `hevc_omx_dec`, which depend on the Kirin platform.
Copying the launchers alone does not supply their runtime or a MateBook decoder.

Experiment 071 established that these are the effective original-image adapters,
and that their original init-managed helpers repeatedly exited with status 1.
The exact failed shell test was not observed; loader absence is not established.

The Linux Compatibility Platform's AnCo codecs serialize application IPC; they
are not video decoders. HarmonyMac's graphics path is useful for the original
RenderService / buffer queue / composer integration, but the inspected Mesa
builds disable video codecs. Neither reference supplies a drop-in decoder for
the effective L410 video sockets. Keep the three references' roles distinct.

## Implementation

`next-experiment/commercial-software-codec-helper-072.c` uses public FFmpeg 8
send/receive APIs with the real native `h264` and `hevc` software decoders.
It retains the original 32-byte request / 64-byte response layout, complete
access-unit input, timestamps and planar YUV420P output.

- H.264: 64 MiB output, four 16 MiB slots, explicit release and backpressure.
- Legacy HEVC: 32 MiB output, single-buffer lifetime, no new protocol flags.
- Padded owned packets prevent input reuse from invalidating decoder references.
- No output slot is overwritten while locked. Full slots consume no input and
  do not harvest/drop a pending decoded frame.
- Peer UID must exactly match the launcher argument (1013 in HarmonyOS).
- Reject malformed packets, unexpected FD counts, truncation, insufficient
  backing storage, aliased input/output files and invalid releases.
- No private FFmpeg fields, OMX device calls, fabricated output or success stubs.

The RAM overlay adds a private runtime directory and replaces only two old
helper launcher paths. It retains the effective original adapters, original
init service definitions, credentials and original authentication checks.
Original HAP resources from 070 and full-frame capture from 068 remain intact.

## Native Ubuntu Validation

Matching FFmpeg development packages were downloaded and extracted privately.
No host packages were installed; the package database and boot ID were checked.

Both normal and ASan/UBSan builds compile with `-Wall -Wextra -Werror`.
All eight exact original HAP videos passed through the socket/memfd helper:
1980 frames, every frame MD5 and reordered presentation timestamp matched the
independent FFmpeg baseline. There were 148 deliberate full-ring backpressure
checks, 14 malformed-request rejection cases, an FD-leak check after malformed
clients, and an exact-peer-UID rejection test. No sanitizer error was reported.
Process termination was by SIGTERM; this is not an exit-time leak-sanitizer claim.

The isolated normal helper/runtime repeated the full 1980-frame test successfully.
Its initial fixture failed because the socket pathname was 108 bytes; it was
preserved, and the shorter-path retry uses a separate `isolated-r2` evidence
directory. The helper binary and source were unchanged for that retry.

See `commercial-software-codec-helper-test-072/result.json`,
`commercial-software-codec-helper-test-072-isolated-r2/result.json` and
`commercial-software-codec-bundle-072/result.json` under this directory.

## Boot Packaging

The initial gzip install was refused before ESP writes by the existing space
guard. That failed staging journal/stdout/stderr and all gzip artifacts remain.
The target kernel image and its exact recorded configuration were hash checked;
`CONFIG_RD_XZ=y` permits XZ/CRC32 recompression without changing archive bytes.
The installed XZ overlay is 45,111,416 bytes, SHA256
`861bfd109e434d9bad3b1596ea2a0ecd50eb00c6d873006215dcf81a59adad8a`.
The 32 MiB free-space guard was retained. No historical/shared payload was deleted.

These native Ubuntu tests and packaging checks do not establish HarmonyOS video
integration, a visible desktop, or normal interaction. Operational conclusions
must come from the unique 072 run, original-service logs and full-frame evidence.
