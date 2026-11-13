# Original configuration API: experiment 083

## Actual result

The separate diagnostic process called the original public `GetCfgFiles("profile")`
API. At samples 17 and 29 it returned `/usr/system/profile`, successfully opened
that directory (158 entries, 154 JSON files), and read all 459 bytes of the genuine
`installs.json`, including SA511 and its original on-demand configuration. Both
diagnostic children exited normally.

This caller explicitly identified itself as UID0, **not SAMGR**. Its success does
not prove SAMGR's own selection, access or parser acceptance. No replacement SA
profile, fabricated database, service identity or permission bypass was introduced.
The original SAMGR/profile-table discrepancy remains unresolved.

## Evidence and preservation

- Independent evidence: `reports/original-graphics-boot-083-independent.json`.
- Serial SHA-256:
  `8e8a18c046302db78be736003b9f7557f1072c0df19cca502a2c1082865f40cd`.
- The helper's actual initrd bytes were independently hash-verified, along with
  all 12 provider ELFs, real ashmem module, initrd, virtual kernel, all three
  original SDK images and 378 previous native raw logs.
- The real hotplug callback completed; no Foundation critical fault or guest
  reboot was observed within the bound. Desktop/readiness/physical scanout remain
  unverified. This experiment used the isolated virtual display, not MateBook DRM.
- No MateBook/Ubuntu or host security changes were performed.

## Remaining diagnostic boundary

Follow actual original SAMGR selection/parse/registration evidence. Do not infer
permission rejection from return 1002, infer parser acceptance from a readable
file, or manually manufacture the BMS directory/database. Existing signature,
privilege-extension and syscap failures remain separate, unrelaxed checks.
