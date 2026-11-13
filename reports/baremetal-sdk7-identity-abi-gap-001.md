# SDK 7 identity ABI gap — read-only findings

## Scope

Bare-metal preparation for SC8280XP MateBook E Go. No kernel patch applied,
no boot entries changed, no native boot attempted, and no SDK image modified.
This is an ABI inventory, not a compatibility or authorization claim.

## Evidence

- Original SDK `system.img`, extracted read-only to WSL
  `/home/zoinve/harmony-virgl-883/baremetal-sdk-identity-inspect-001`.
- `baremetal-sdk-identity-disassembly-001.txt`: original library exports and
  disassembly; `baremetal-sdk-access-ioctl-001.txt`: targeted access SDK evidence.
- `libtokensetproc_shared.z.so` has the device string `/dev/access_token_id`
  at ELF virtual address `0xb68` (also file offset `0xb68`). Its SPM routines
  load this address immediately before `open(O_RDWR)`.
- `SpmAddEntries` at `0x2220` constructs request `0xc0084110` and passes it
  through the shared implementation; `SpmSetEntries` constructs `0xc0084111`
  and branches to that implementation at `0x222c`.

## Observed requests

All listed requests use ioctl type `0x41` (`A`). Sizes below are the encoded
ioctl sizes, not independently verified complete pointed-to payload layouts.

| Export | Request | Encoded bytes |
|---|---|---:|
| GetSelfTokenID | `0x80084101` | 8 |
| SetSelfTokenID | `0x40084102` | 8 |
| GetFirstCallerTokenID | `0x80084103` | 8 |
| SetFirstCallerTokenID | `0x40084104` | 8 |
| GetParentHapTokenID | `0x80104109` | 16 |
| SpmAddEntries | `0xc0084110` | 8 |
| SpmSetEntries | `0xc0084111` | 8 |
| SpmGetEntry | `0x80d84112` | 216 |
| SpmRemoveEntry | `0x40044113` | 4 |
| SpmIncUidRefCnt / SpmDecUidRefCnt | `0x400c4114` | 12 |
| SpmGetUidRefCnt | `0x80104115` | 16 |
| SpmIncTokenidRefCnt / SpmDecTokenidRefCnt | `0x400c4116` | 12 |
| SpmGetTokenidRefCnt | `0x80104117` | 16 |
| SpmClearSpawnidRefCnt | `0x40044118` | 4 |
| SpmGetVersion | `0x80044119` | 4 |

The original `libaccesstoken_sdk.z.so` also contains requests `0x400c4107`
and `0x80084101`. Stripped hidden-function boundaries must not be inferred
from the nearest exported symbol name.

## Consequences and limits

- The local reference access-token driver implements commands 1–8 only;
  a clean patch dry run does not establish SDK 7 compatibility.
- The new parent-token and SPM interfaces require authoritative structure,
  lifetime, concurrency, and permission semantics before implementation.
- Earlier VM `magic fail TYPE=84` messages remain unexplained by this evidence;
  these observed `A` requests are type 65, not type 84 (`T`).
- Export names and ioctl encoding alone do not establish when each request is
  required during native startup, or prove the cause of earlier account failures.
- Do not replace missing commands with success stubs, fabricated token IDs,
  permissive permission responses, or edited authentication databases.

## Current local search

Targeted searches found only the existing reference `access_tokenid.c/.h`
under the OpenCode temporary reference directory. Neither the known WSL
Harmony graphics sources nor a filename search in `D:/lab/MacOS_ego` located
the SDK 7 SPM driver. These bounded searches are not proof it is absent from
all local storage.
