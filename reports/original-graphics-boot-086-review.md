# Original SAMGR syscall audit 086

## Result: accepted rule, insufficient capture

- The guest kernel acknowledged the UID5555/AArch64 logging rule with error0.
  The existing audit receiver was not replaced. Original SAMGR PID131 retained
  UID5555 and `u:r:samgr:s0`.
- Independent verification preserved 81 attributable syscall records, all
  successful `openat` calls. Some associated paths were
  `/sys/fs/selinux/context`; none of these records establish the result of
  opening or enumerating the SA profile directory.
- Logging was severely incomplete: printk suppression and `audit_lost`
  counters started during early boot; the final observed lost count was
  127255. The first valid parsed SAMGR syscall was at 37.084 seconds, after
  the early initialization window. Missing profile records therefore do not
  prove missing access, denial, or parser rejection.

Evidence: `reports/original-graphics-boot-086-independent.json` and the
preserved 086 serial log. Serial SHA-256:
`826905e425d5912ce8279dc5b60d4f047a3408715dd26ec81e25d9f4e0885885`.

## Preservation

The independent verifier checked the 12 injected graphics files, genuine
ashmem module, configuration-query helper, initrd, virtual kernel, all three
original SDK images, and 378 prior native raw files. No original profile,
database, service identity, permission check or audit receiver was changed.
This was a local isolated WSL/QEMU experiment; no MateBook/Ubuntu boot,
security, or screen settings were touched. Desktop and physical scanout
remain unverified. Completed 086 was not rerun.

## Next experiment: 087, pending

087 retains the same original graph and UID-scoped logging rule, but subscribes
to kernel `AUDIT_NLGRP_READLOG` copies before original init executes. This
subscriber sends no audit control requests and does not register itself as the
audit receiver. It writes only a new 0600 diagnostic file on disposable guest
data, bounded to 60 seconds / 64 MiB; truncation, socket losses, write errors
and the byte limit are reported rather than treated as complete evidence.

Preparation compiled successfully. Init is 854728 bytes, SHA-256:
`cfe2c9155d00b6f633591254d153875b536c519315ed3afa207ddd7a62a70010`.
Three explicit offline safety/parser tests passed, including preservation of
negative syscall returns and hexadecimal audit paths. Extraction is designed
to repair only an exclusive clone of disposable scratch, never its retained
source or an original SDK image.

087 is running at the time of this note. Receiver setup, capture quality,
profile access, SA511 registration and desktop recovery are not yet claimed.
