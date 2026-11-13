# Original profile loading: observation 085 and scoped audit 086

## Verified 085 evidence

- `original-graphics-boot-085-independent.json` independently verifies the original
  SDK images, kernel, initrd, twelve injected graphics libraries, real ashmem
  module, configuration-query executable and all 378 retained native raw files.
- Serial SHA-256:
  `ccd103a88d331065444a589b722fdad0b82d23c9c63bed6ad2c5b95e82d7f841`.
- Notification-only fanotify initialization, directory mark and observer fork
  succeeded. Original SAMGR PID133 was independently identified as UID5555,
  domain `u:r:samgr:s0`, with no incomplete identity rows.
- 161 parsed file events include genuine accesses by other services and the
  explicitly separate root diagnostic. None were attributed to SAMGR. This is
  **not proof that SAMGR never enumerated or accessed profiles**: the mark did
  not request directory events, and complete capture cannot be established.
- Original graphics hotplug completed; Foundation critical failure and guest
  reboot were not observed within the bounded run. Desktop readiness remains
  unverified; the virtual screenshots do not establish a working desktop.

## Read-only follow-up

`original-directory-utils-001/result.json` records an independent read-only audit
of the genuine `libutils.z.so`, without executing it or changing the system image.
Its `GetDirFiles` enumerates names using `opendir`/`readdir` and does not need to
open individual JSON files merely to build the filename list. The negative
child-file observations therefore cannot distinguish failed directory traversal
from later parsing or registration.

Original SAMGR entry disassembly calls `SystemAbilityManager::Init`, then
`BaseSystemAbilityManager::Init`; the latter contains the previously identified
profile-initialization call. Earlier exploratory wording calling this last
region a constructor was inaccurate. Static call paths are not runtime proof.

## Fresh experiment 086 — running, no outcome yet

The fresh guest enables Linux audit logging with `audit=1` and attempts to add
one syscall exit-logging rule scoped to AArch64 UID5555: `openat`, `getdents64`
and `faccessat`. It does not replace the audit receiver, remove rules, change
authorization decisions, edit profiles, create a database or change identities.
Actual kernel acknowledgments, return codes and any capture-loss messages must
be retained; missing records will not be treated as proof of missing access.

Preparation succeeded once. Init SHA-256:
`0b42ec50ca79aec43a0834d8c81167d6268531440492bef43fda49f49d40ee69`.
Original policy and graphics-init configuration hashes remain unchanged.
The explicit offline audit suite passed 3 tests. Runtime is bounded to 480s,
with the same read-only SDK images, RAM userdata, working graphics stack and
virtual-only scanout. Runtime verification is pending automatic completion.

All work remains local to the isolated WSL guest. No MateBook SSH session,
Ubuntu boot/security/screen change, original-image write or permission bypass
was performed. Completed experiments and evidence were not rerun or overwritten.
