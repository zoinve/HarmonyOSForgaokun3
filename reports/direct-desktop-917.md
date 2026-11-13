# 917: normal ability-manager client results

Ordinary shell UID/GID 2000, SELinux `sh` domain, effective capabilities zero.
The diagnostic preload forwards original functions once and preserves results:

- Product ability-manager client `Connect`: 0.
- SceneBoard `StartAbility`: 2097205 (`ERR_INVALID_CALLER` in public API sources).
- Guide `KillProcess`: 1; failure, not successful termination.
- Guide PID 6690 remained unchanged through all three observations.

Neither activation nor a genuine desktop has been verified. No certificates,
caller tokens, account/trust databases or service identities were fabricated.
917 was asked to quit normally; lifecycle integrity is recorded separately.

Next bounded test uses the original HDC TCP trigger and normal authentication.
Payload 918 SHA-256:
`0a2855dafa08ea5970cfaa02765233d5e4f90c0a1b102be7092c7457d05e6200`.
It queries developer/authentication state; it does not force developer mode,
disable HDC authentication, or grant permissions. Optional host ingress binds
only to `127.0.0.1:18818`, forwarding to the guest's original TCP port 8710.
