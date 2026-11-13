# Original graphics boot 089 — canonical system layout

## Verified outcome

The canonical `/system` readonly bind of the same original system tree fixed a
specific early SAMGR path-visibility failure. In 087, genuine SAMGR UID5555
`faccessat("/usr/system/profile")` returned ENOENT. In 089, genuine SAMGR PID134
`faccessat("/system/profile")` returned zero and `openat` returned FD11. Two
same-audit-serial records also show successful opens of the original
`/system/profile/installs.json`. These are actual original-process results, not
the separate root diagnostic helper's view.

The new bind preserves READONLY and NODEV; profile files, priorities, original
service credentials and policy were not rewritten. Candidate088 remains an
unbooted, preserved build because its reviewed bind remount omitted NODEV.
Existing volatile graphics overlays are unchanged; this does not assert every
final overlay has the lower bind's flags.

## Remaining failure

Original Foundation/BMS logs now include `rdb open` and shared-bundle metadata
work. No independent database-file inspection has been performed, so this is
not a claim that a particular database file was created or all SA511 startup
steps completed.

`GetForegroundOsAccountLocalId` still reports 4194349. Original `bm` and `aa`
commands still report business failure despite zero child exit status; `aa`
reports generic internal error10108101. Neither error establishes a permission
or memory cause. Other original bundle/syscap/signature checks remain intact.

All four QMP captures (120/240/360/450 seconds) are black 1280x800 RGB images,
pixel SHA256 `76ed5c9c326ba62322d464a22d3fcf7b76c7352c6d33badc36ccea7a33325e97`.
Lossless PPM/PNG consistency was independently verified. No desktop, physical
scanout or interactive readiness is claimed. No Foundation critical fault or
guest reboot was observed within the bound.

## Evidence and preservation

- `reports/original-graphics-boot-089-independent.json`
- `reports/original-audit-copy-089/` — extraction from a recovery clone only
- Serial SHA256: `543c1a5ee1a318f599d51ce5d279446a3550ad4f3be2861c563362209a4a78fe`
- 42 observed SELinux samples were permissive; policy support/loading retained.
- All twelve injected provider files, genuine ashmem module, config-query helper,
  initrd, kernel and three full original SDK images independently hash-checked.
- All 378 historical native raw-file hashes were verified unchanged.

Audit copies remain bounded and incomplete; positive complete records are not a
claim of exhaustive syscall coverage. Recovery repaired only a new clone of
disposable guest scratch, never original images or the retained source scratch.
No completed experiment or successful verifier was rerun. No MateBook/Ubuntu
host boot, security or screen settings were changed; this remains local WSL VM
evidence only.

## Next observation 090 (running at writing)

Use the pre-audit083 diagnostic baseline with the verified canonical readonly
NODEV bind. This omits the heavy audit/fanotify collectors, retaining the same
original services, providers005/EGL009, ashmem module and virtual kernel. Query
the discovered original account-manager PID and late Foundation logs with the
original `hilog -z 200 -P` tool. Original `bm`/`aa` requests and QMP captures
remain unchanged; no account, database or identity is fabricated.

New offline tests: two account-observation gates and six inherited config/layout
gates passed. Preparation090 compiled successfully; init853208 bytes SHA256
`199cb6d24414a50fdcc184a30886c6d7ecfefd7c4aed939573a3cdeefad94c92`.
Policy and graphics-init configuration hashes remain unchanged. Runtime090 has
no outcome yet; its independent verifier has not been executed.
