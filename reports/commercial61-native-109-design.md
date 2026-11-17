# Original memory-service diagnostic 109: preparation

Status: offline audit and observer prepared; no candidate built, installed or booted.

108 genuinely progresses past the original namespace wrapper into memmgrservice,
but all seven original CheckSystemAbility observations find SA1909 absent. The
desktop query remains blocked and original guide recovery still occurs.

## Original branch evidence

The supplied library SHA256 is
`2cf2566bb7bf580513e82c6d1819775886cfe3ecd35a5e2b14a0eae60dceb012`.
Read-only extraction, symbols, full disassembly ranges and branch addresses are
preserved in `memmgr-initialization-audit-109/flow-analysis.json`.

`OnStart` calls `Init` at 0x19b100 and branches away from Publish on false at
0x19b104. Publish is called at 0x19b12c; its own failure is checked at 0x19b150.
Init checks both reclaim-priority and reclaim-strategy initialization. The latter
checks root memcg setup. These are static paths, not proof of which runtime branch
was taken. The early accessToken IPC error is not established as the cause.

## Planned additional observation

`commercial-memmgr-stack-109.sh` checks the byte-identical original DFX probe,
waits boundedly for one original memmgrservice, captures its threads at first
observation and again 20 seconds after the first capture/namespace survey, and
refuses a changed or ambiguous target. Each original DFX call has a 12-second
bound. It reads mountinfo and memcg directory metadata through that service's
own proc root; it does not substitute the observer's namespace for the service's.

The first capture may miss fast initialization. A late stack cannot prove an
earlier failing branch. Native DFX observation can perturb timing. Neither a
successful capture nor PID presence establishes SA publication or desktop.

## Integration requirements before any boot

- Keep 108's real directory scaffolding and original runtime integrity checks.
- Export the new dedicated log explicitly and verify exact archive/source diff.
- Preserve original service config, tokens, namespace wrapper and recovery.
- Preserve full-resolution frame pair and input correlation, not only service logs.
- Admit/build/install once under immutable numbered evidence, archive old entry
  before retaining only latest two, then bounded single boot and serial retrieval.
- Recheck actual SA1909 and OOBE independently; the desktop goal remains active.

Do not create fake kernel nodes or memory metrics, suppress initialization
failures, bypass Publish checks, or fabricate identity/setup/activation state.
