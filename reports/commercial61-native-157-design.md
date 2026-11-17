# Native authenticated diagnostic sidecar 157

This candidate preserves the full working 153 baseline and adds an optional
read-only diagnostic transport. It does not repair Settings installation or
claim complete process debugging or hardware acceptance.

## Exact delta

- Outer static init includes `native-live-debug-157.h`: optional hash-checked
  package extraction, one asynchronous start after the Wi-Fi starter succeeds,
  and cleanup before the original target is stopped.
- Its existing early wrapper changes only the expected outer-init hash.
- Adds the statically linked Linux launcher `/live-debug157` and empty RAM
  directory `/live-debug157-root`.
- All original runtime/bootstrap/native-target files, native libraries,
  services, data seed, input/USB modules, kernel and DTB remain unchanged.
- Complete 28-archive boot chain was merged and compared with the full candidate.

## Authentication and isolation

The on-device tools archive is 6,147,756 bytes, SHA-256
`f83599ea0441395f62a6b2bb9e6097dcef069db2d0f12399b564857a144daca7`.
It contains the same native OpenSSH closure and reader tested in 156, with a
fixed LAN listen address. It contains no private key, no special device node,
no symlink, no original image and no raw test log.

The new diagnostic host key remains in root-owned on-device storage, outside
the ESP. Only the native launcher reads and copies it into its RAM root.
Client host-key pinning reuses its public key obtained through trusted Ubuntu SSH.
Only the existing workstation public key is authorized. Password authentication,
keyboard-interactive authentication, PTYs, forwarding and user startup scripts
are disabled. The forced reader permits only three fixed read-only commands.

The launcher requires root, the explicit native/debug kernel opt-ins, the actual
MateBook model, a RAM-backed diagnostic directory and a distinct target network
namespace with the expected WLAN address. It does not join HarmonyOS's mount
or PID namespace. It creates separate mount/PID namespaces and a diagnostic root,
with only two already-captured log inodes bind-mounted read-only. No HarmonyOS
filesystem or original-image mount is exposed inside the SSH root.

The SSH PID namespace is bounded to 90 seconds after launch, with an independent
115-second outer launcher bound and parent-death protection. Termination of its
namespace init kills remaining SSH descendants even if they created sessions.
Existing native automatic-return and blocked-kernel limitations remain unchanged.

Listener: 192.168.10.210:22257, only if that address is actually present on wlan0.
No fallback to an unverified address, wildcard listener or authentication bypass.

## Verification scope

Admission passed ten focused/baseline test scripts, static helper/native entry
guards, exact delta/hash checks, secret-path exclusion, workflow preservation
checks and full boot-chain equality. Separate analysis tests reject a successful
client without matching original network-namespace evidence or growing logs.

Native acceptance additionally requires a pinned, authenticated client session,
completed follow protocol, measured log growth, rejection of arbitrary shell
commands, and matching original target namespace evidence. Merely spawning sshd,
seeing a port, or passing the Ubuntu fixture does not meet this condition.

One operational boot is authorized by the existing continuous-work scope;
there are no automatic boot retries. Ubuntu remains the persistent default.
Entry retention keeps 153/157 and archives the removed 152 entry outside the ESP.
Original images, firmware, historical evidence and enabled/active screen-off
timer remain preservation requirements.
