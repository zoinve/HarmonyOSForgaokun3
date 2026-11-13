# Original SAMGR profile observation 081

## Verified result

The original SAMGR process (PID132) could read its genuine
`/system/profile/installs.json`: both sampled process-root reads returned all
459 bytes without error. The unchanged JSON describes process `installs`, SA511,
`libinstalls.z.so`, and on-demand rather than run-on-create activation.

Nevertheless, actual original SAMGR logs repeatedly reported
`LoadSystemAbility SA:511 not supported!` and return1002. The read-only audit of
the matching original SAMGR binary confirms that this return follows failed
`GetSaProfile`, not a permission-denied branch. File visibility therefore does
not establish selection or successful parsing into the loaded profile table.
The reason this original profile was not loaded is still unverified.

This matters because the original BMS delegates directory creation to the
original installs service. No replacement profile, BMS database, manual BMS
directory, fabricated identity, or authorization bypass has been introduced.
Separate original signature, extension-privilege and syscap errors remain intact.

## Preservation and limits

- Independent evidence: `reports/original-graphics-boot-081-independent.json`.
- Serial SHA-256:
  `cac490e54f9972e87deebd57fd5e3e2c473587b314ee125511122cd3ea289313`.
- All48 observed SELinux samples were permissive; no Foundation critical fault
  or guest reboot was observed within the bounded run.
- Independently verified all three original SDK image hashes, all12 injected
  provider ELF files, genuine ashmem module, initrd, virtual kernel and378 prior
  native raw files. Neither the original images nor historical evidence changed.
- This remains an isolated software-rendered virtual-display test, not a native
  HarmonyOS desktop or physical scanout result. Readiness/desktop remain false.
- No MateBook/Ubuntu operations or fresh host-screen checks were performed.

## Next controlled observation

082 keeps the services, profiles, providers, credentials, policy and VM settings
unchanged. It adds bounded calls to the original `param get` for
`const.cust.config_dir_layer` and `const.cust.follow_x_rules`, retaining real
output, failures and wait status. It was launched once and is pending at the time
of this record. No outcome or configuration fix is claimed in advance.
