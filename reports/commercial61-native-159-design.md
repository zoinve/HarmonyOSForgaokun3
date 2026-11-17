# Native 159: authenticated read-only runtime observation

The basic-driver objective remains active, with touchscreen and USB priority.
This candidate adds diagnostic transport only; no driver or Settings repair is
claimed. Original services, kernel, DTB, modules, images, runtime and desktop
seed remain unchanged. Candidate 158 remains unbooted and its records immutable.

## Prerequisite evidence

- Native 157 stopped at the original-init path guard, before starting SSH.
- Root-anchored openat2 regression 158 handles the absolute /system link.
- Address selection/config tests 159 reject absent, ambiguous and invalid WLAN
  addresses and create an exclusive RAM diagnostic configuration only.
- reports/live-debug-discovery-159 contains a build-only compiler failure; no
  target test started in that attempt. No failed evidence was overwritten.
- reports/live-debug-discovery-159-compile-fix-1/result.json proves a single
  bounded native ARM64 Ubuntu UDP fixture. Windows discovered 192.168.10.128
  by broadcast, malformed queries received no replies, the listener stopped,
  and addresses/routes/boot ID/original SSH config and activity were preserved.
  This is not HarmonyOS runtime or SSH-authentication evidence.

## Runtime scope

- Join only the genuine HarmonyOS network namespace; create separate diagnostic
  mount/PID namespaces and RAM root. Preserve original service/linker identities.
- Select the one actual up wlan0 address in the observed lab subnet. Generate a
  new sshd_config.live, preserving public-key authentication and ForceCommand.
- SSH listens only on that actual address, port 22257. Private host key remains
  on-device and is copied into RAM, never into an archive or the ESP.
- UDP discovery port 22259 is device-bound to wlan0. Broadcast reception uses
  INADDR_ANY only for UDP, with incoming interface/local destination validation.
  Only workstation sources 192.168.10.201/.248 with nonprivileged ports qualify.
  Queries have exact size/format and a nonce; replies contain only nonce/address/
  SSH port, are smaller than queries, limited to one per second and 32 total.
- Discovery is untrusted. The client must still authenticate the pinned host
  key and existing workstation public key. It never accepts an unknown host key.
- Reader exposes only fixed status/settings/follow-settings operations with
  fixed event names. No raw input, USB serial, arbitrary log or shell export.
- Namespace PID1 owns all SSH/discovery descendants. Original independent
  90/115-second supervision and the bounded native auto-return remain intact.

## Acceptance

Admission passed 14 focused/baseline scripts, exact helper regeneration and
byte-identical static recompilation, non-native refusal guards, and complete
28-archive ordered-chain equality. Original shared driver/service artifacts
match the parent. Admission does not imply an actual live connection.

Runtime acceptance requires matching original and diagnostic target/net inode,
the same actual address in native context and authenticated client, log growth
during observation, completed follow protocol, shell refusal, and clean namespace
and supervisor reaping. Retrieval hashing and Ubuntu/image/EFI/default/firmware/
screen-off preservation verification must follow a single bounded boot.
Full process debugger attachment and physical input/USB service acceptance
remain independent requirements and must not be inferred from transport success.
