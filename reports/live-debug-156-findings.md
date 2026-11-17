# Authenticated diagnostic transport fixture 156

## What was actually verified

This was a separate native ARM64 Ubuntu loopback test, not a HarmonyOS boot
and not a live HarmonyOS debugger connection. The fixture was stopped after testing.
It does not resolve the unsigned Settings package identified by analysis 155.

- Reused the device's unchanged OpenSSH server, its auth/session executables,
  and their exact dynamic dependency closure inside a new diagnostic chroot.
- A new fixture host key was generated on-device. Its public key was obtained
  through the already trusted Ubuntu SSH connection and pinned for the client.
  No existing host private key was read or copied; the new private key was not exported.
- Accepted only the existing workstation's Ed25519 public key. Password and
  keyboard-interactive authentication were disabled.
- Actual authenticated client connections ran the native statically linked
  forced reader successfully. Its SHA-256 is
  `2496354535c0789f29d90949ad9051e44da371636fd18d7977248fc48faadfc4`.
- Rejected `sh`, `status; id`, a newline-injected command, and `scp -t file`
  with exit 77. A client without public-key authentication was denied.
  Actual port-forward requests were denied as administratively prohibited.
- Listener was restricted to 127.0.0.1:22256, reached through an authenticated
  temporary Ubuntu SSH tunnel. No LAN-facing diagnostic listener was started.
- The server had an independent 180-second outer deadline and was explicitly
  stopped after the checks; the temporary client tunnel was also terminated.

## Reader scope and tests

`next-experiment/live-debug-reader-156.c` accepts only `status`, `settings`,
and `follow-settings` via the configured forced-command invocation. It never
executes a caller-provided command. Paths are fixed; symlinks and non-regular
log files are rejected. It reads at most 2 MiB, with a 30-second follow limit.

Settings output contains fixed event names, not raw log lines. Fixture tests
verify that arbitrary keyboard/serial-like text does not leave the reader.
The native authenticated transport test used explicitly synthetic input;
its Settings events are not presented as another HarmonyOS failure or success.

Five unit tests passed, including command rejection, output privacy,
symlink/FIFO rejection, bounded live append following, and oversized/binary lines.
The live-follow test ran on the build host; native ARM64 SSH verified the
snapshot/status and negative access checks, not native real-time following.

## Preservation and evidence

- `live-debug-156/result.json`: client assertions and explicit non-Harmony labels.
- `live-debug-156/preparation.json`: exact source hashes, configuration and effective sshd settings.
- `live-debug-156/known_hosts`: fixture public host key only.
- `live-debug-156/stop.json`: shutdown and original daemon log.
- `live-debug-156/post-fixture-verification.json`: all 22 copied source/closure
  hashes still match, reader hash matches, listener absent, original SSH active.
- Ubuntu boot ID remains `6643a37b-af4b-4656-af53-d6538bdf93b7`.
  Default boot remains Ubuntu, and the screen-off timer remains scheduled.
- No existing SSH service configuration, boot entry, original HarmonyOS image,
  firmware, developer-mode setting, signature policy or native service was edited.

## Remaining native integration

The authoritative current native init source clones HarmonyOS with its own
PID, mount **and network** namespaces, then moves phy0 into that network namespace.
Starting a listener in the outer namespace would not expose it through the
observed native WLAN address. Network-namespace attachment must be implemented
and tested, not assumed from Ubuntu-loopback success.

Next integration should load the verified tools into a separate RAM diagnostic
root, join only the target network namespace, bind only the already captured
diagnostic files read-only, and retain a hard supervisor deadline and cleanup.
Keep all private keys outside the ESP and all glibc dependencies outside the
original HarmonyOS linker namespace. Do not replace HDC or bypass its original checks.
Full process attachment, native live following and hardware-service acceptance
remain unverified.
